import hashlib
import logging
import os
import re
from datetime import date, datetime, timedelta
from typing import Iterable
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

from users.models import CompanyProfile, User

from .models import InternshipOffer
from .scraper_ai import enrich_scraped_offers_with_ai, skills_heuristic_string

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 14
MAX_SOURCE_OFFERS = 30

MOROCCAN_CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir", "Fes",
    "Kenitra", "Temara", "Mohammedia", "Meknes", "Oujda", "Remote Maroc",
]

MOROCCAN_KEYWORDS = {
    "stage", "stagiaire", "pfe", "pfa", "internship", "alternance",
    "junior", "entry level", "graduate", "casablanca", "rabat", "marrakech",
    "tanger", "agadir", "fes", "kenitra", "maroc", "morocco", "remote maroc",
}

DEFAULT_SEARCH_TERMS = [
    "stage developpeur",
    "stage pfe informatique",
    "stage data analyst",
    "stage react django",
    "emploi junior developpeur maroc",
]

DEFAULT_MOROCCAN_OFFERS = [
    {
        "title": "Stage PFE Developpeur Full Stack Django React",
        "description": (
            "Societe basee a Casablanca recherchant un stagiaire PFE pour contribuer au "
            "developpement d'une plateforme SaaS. Stack: Python, Django, React, PostgreSQL, Git."
        ),
        "location": "Casablanca",
        "offer_type": "stage",
        "duration_months": 6,
        "source_url": "https://www.rekrute.com/offres-stage-casablanca-fullstack",
        "source_platform": "Rekrute",
        "published_date": date.today() - timedelta(days=2),
    },
    {
        "title": "Stage Data Analyst BI - Rabat",
        "description": (
            "Stage de fin d'etudes a Rabat autour de l'analyse de donnees, tableaux de bord Power BI, "
            "SQL et Python pour une equipe produit orientee data."
        ),
        "location": "Rabat",
        "offer_type": "stage",
        "duration_months": 4,
        "source_url": "https://www.emploi.ma/offre-stage-data-analyst-rabat",
        "source_platform": "Emploi.ma",
        "published_date": date.today() - timedelta(days=4),
    },
    {
        "title": "Stage Mobile Flutter - Marrakech",
        "description": (
            "Startup digitale a Marrakech recherchant un stagiaire Flutter/Dart pour faire evoluer "
            "une application mobile connectee a des API REST."
        ),
        "location": "Marrakech",
        "offer_type": "stage",
        "duration_months": 3,
        "source_url": "https://www.dreamjob.ma/stage-flutter-marrakech",
        "source_platform": "Dreamjob",
        "published_date": date.today() - timedelta(days=1),
    },
]


def _normalize_text(value: str) -> str:
    value = (value or "").lower()
    value = re.sub(r"[^\w\s\+\#\.\-/]", " ", value)
    return " ".join(value.split())


def _slug(value: str, fallback: str = "source") -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", _normalize_text(value)).strip("_")
    return (slug or fallback)[:80]


def _is_moroccan_offer(offer: dict) -> bool:
    haystack = _normalize_text(
        f"{offer.get('title', '')} {offer.get('description', '')} {offer.get('location', '')}"
    )
    return any(keyword in haystack for keyword in MOROCCAN_KEYWORDS)


def _looks_relevant_offer(offer: dict) -> bool:
    haystack = _normalize_text(
        f"{offer.get('title', '')} {offer.get('description', '')} {offer.get('location', '')}"
    )
    noisy = ["senior manager", "directeur", "director", "lead principal"]
    if any(token in haystack for token in noisy):
        return False
    return any(
        token in haystack
        for token in [
            "stage", "stagiaire", "pfe", "pfa", "internship", "alternance",
            "junior", "graduate", "entry level", "developpeur", "developer",
            "data", "analyst", "software", "frontend", "backend", "full stack",
        ]
    )


def _detect_offer_type(payload: dict) -> str:
    haystack = _normalize_text(f"{payload.get('title', '')} {payload.get('description', '')}")
    if "freelance" in haystack:
        return "freelance"
    if any(token in haystack for token in ["cdi", "cdd", "emploi"]):
        return "emploi"
    return "stage"


def _detect_location(text: str) -> str:
    haystack = _normalize_text(text)
    for city in MOROCCAN_CITIES:
        if _normalize_text(city) in haystack:
            return city
    return "Maroc"


def _parse_date(text: str) -> date | None:
    if not text:
        return None
    normalized = _normalize_text(text)
    if "aujourd" in normalized:
        return date.today()
    if "hier" in normalized:
        return date.today() - timedelta(days=1)

    match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", normalized)
    if match:
        day, month, year = match.groups()
        year = f"20{year}" if len(year) == 2 else year
        try:
            return datetime(int(year), int(month), int(day)).date()
        except ValueError:
            return None
    return None


def _fetch_html(url: str) -> str:
    response = requests.get(
        url,
        timeout=REQUEST_TIMEOUT,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PlateformeStagesBot/1.0)",
        },
    )
    response.raise_for_status()
    return response.text


def _parse_json_ld_jobs(soup: BeautifulSoup, base_url: str, platform: str) -> list[dict]:
    offers: list[dict] = []
    for node in soup.select('script[type="application/ld+json"]'):
        raw = node.string or node.get_text("", strip=True)
        if not raw:
            continue
        try:
            import json

            payload = json.loads(raw)
        except Exception:
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            graph = item.get("@graph")
            if isinstance(graph, list):
                items.extend([x for x in graph if isinstance(x, dict)])
                continue
            if item.get("@type") != "JobPosting":
                continue
            title = item.get("title") or ""
            desc = BeautifulSoup(item.get("description") or "", "html.parser").get_text(" ", strip=True)
            hiring = item.get("hiringOrganization") or {}
            location = item.get("jobLocation") or {}
            if isinstance(location, list):
                location = location[0] if location else {}
            address = location.get("address") if isinstance(location, dict) else {}
            city = ""
            if isinstance(address, dict):
                city = address.get("addressLocality") or address.get("addressRegion") or ""
            source_url = item.get("url") or base_url
            offers.append({
                "title": title,
                "description": desc or title,
                "location": city or _detect_location(f"{title} {desc}"),
                "company_name": hiring.get("name") if isinstance(hiring, dict) else "",
                "source_url": urljoin(base_url, source_url),
                "source_platform": platform,
                "published_date": _parse_date(str(item.get("datePosted") or "")) or date.today(),
                "offer_type": _detect_offer_type({"title": title, "description": desc}),
            })
    return offers


def _parse_rekrute(search_term: str = "stage") -> list[dict]:
    url = f"https://www.rekrute.com/offres.html?s=1&keyword={quote_plus(search_term)}"
    try:
        html = _fetch_html(url)
    except Exception as exc:
        logger.warning("Scraping Rekrute indisponible: %s", exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    offers: list[dict] = _parse_json_ld_jobs(soup, url, "Rekrute")
    cards = soup.select(".post-id, .result, .section, article, .job")
    for card in cards[:MAX_SOURCE_OFFERS]:
        title_node = card.select_one("h2 a, h3 a, .titreJob, a[href*='offre-emploi']")
        desc_node = card.select_one(".description, .job-description, .info, p")
        location_node = card.select_one(".location, .lieu, .city")
        company_node = card.select_one(".company, .nomEntreprise, .recruiter, .info span")
        link = title_node.get("href") if title_node else None
        if not title_node:
            continue
        title = title_node.get_text(" ", strip=True)
        description = desc_node.get_text(" ", strip=True) if desc_node else title
        location = location_node.get_text(" ", strip=True) if location_node else _detect_location(description)
        offers.append({
            "title": title,
            "description": description,
            "location": location,
            "company_name": company_node.get_text(" ", strip=True) if company_node else "",
            "source_url": urljoin(url, link) if link else url,
            "source_platform": "Rekrute",
            "published_date": date.today(),
            "offer_type": _detect_offer_type({"title": title, "description": description}),
        })
    return offers


def _parse_emploi_ma(search_term: str = "stage") -> list[dict]:
    url = f"https://www.emploi.ma/recherche-jobs-maroc?keywords={quote_plus(search_term)}"
    try:
        html = _fetch_html(url)
    except Exception as exc:
        logger.warning("Scraping Emploi.ma indisponible: %s", exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    offers: list[dict] = _parse_json_ld_jobs(soup, url, "Emploi.ma")
    cards = soup.select(".job-description-wrapper, .card-job, article, .job")
    for card in cards[:MAX_SOURCE_OFFERS]:
        title_node = card.select_one("h5 a, h3 a, h2 a")
        desc_node = card.select_one(".field-item, .card-job-description")
        location_node = card.select_one(".job-region, .location")
        company_node = card.select_one(".company-name, .job-recruiter, .card-job-company")
        date_node = card.select_one(".job-date, .date")
        if not title_node:
            continue
        title = title_node.get_text(" ", strip=True)
        description = desc_node.get_text(" ", strip=True) if desc_node else title
        location = location_node.get_text(" ", strip=True) if location_node else _detect_location(description)
        offers.append({
            "title": title,
            "description": description,
            "location": location,
            "company_name": company_node.get_text(" ", strip=True) if company_node else "",
            "source_url": urljoin(url, title_node.get("href", "")),
            "source_platform": "Emploi.ma",
            "published_date": _parse_date(date_node.get_text(" ", strip=True) if date_node else "") or date.today(),
            "offer_type": _detect_offer_type({"title": title, "description": description}),
        })
    return offers


def _parse_arbeitnow() -> list[dict]:
    """API publique avec vraies URLs. On garde surtout remote/junior/dev/data."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        jobs = response.json().get("data", [])
    except Exception as exc:
        logger.warning("API Arbeitnow indisponible: %s", exc)
        return []

    offers: list[dict] = []
    for job in jobs[:MAX_SOURCE_OFFERS]:
        title = (job.get("title") or "").strip()
        desc = BeautifulSoup(job.get("description") or "", "html.parser").get_text(" ", strip=True)
        tags = ", ".join(job.get("tags") or [])
        location = job.get("location") or ("Remote" if job.get("remote") else "")
        payload = {
            "title": title,
            "description": f"{desc} {tags}",
            "location": location,
        }
        if not _looks_relevant_offer(payload):
            continue
        created_at = job.get("created_at")
        published = None
        if created_at:
            try:
                published = datetime.fromtimestamp(int(created_at)).date()
            except Exception:
                published = None
        offers.append({
            "title": title,
            "description": desc[:2500] or title,
            "location": location or "Remote",
            "company_name": job.get("company_name") or "Arbeitnow company",
            "source_url": job.get("url"),
            "source_platform": "Arbeitnow",
            "published_date": published or date.today(),
            "offer_type": _detect_offer_type(payload),
        })
    return offers


def _parse_remoteok() -> list[dict]:
    url = "https://remoteok.com/api"
    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 PlateformeStagesBot/1.0"},
        )
        response.raise_for_status()
        rows = response.json()
    except Exception as exc:
        logger.warning("API RemoteOK indisponible: %s", exc)
        return []

    offers: list[dict] = []
    for job in rows[1:MAX_SOURCE_OFFERS + 1] if isinstance(rows, list) else []:
        if not isinstance(job, dict):
            continue
        title = (job.get("position") or job.get("title") or "").strip()
        desc = BeautifulSoup(job.get("description") or "", "html.parser").get_text(" ", strip=True)
        tags = ", ".join(job.get("tags") or [])
        payload = {"title": title, "description": f"{desc} {tags}", "location": "Remote"}
        if not _looks_relevant_offer(payload):
            continue
        offers.append({
            "title": title,
            "description": desc[:2500] or f"Offre remote: {title}. Tags: {tags}",
            "location": "Remote",
            "company_name": job.get("company") or "RemoteOK company",
            "source_url": job.get("url") or f"https://remoteok.com/remote-jobs/{job.get('id')}",
            "source_platform": "RemoteOK",
            "published_date": _parse_date(str(job.get("date") or "")) or date.today(),
            "offer_type": _detect_offer_type(payload),
        })
    return offers


def _build_remote_morocco_offers() -> list[dict]:
    url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=20"
    try:
      response = requests.get(url, timeout=REQUEST_TIMEOUT)
      response.raise_for_status()
      jobs = response.json().get("jobs", [])
    except Exception as exc:
      logger.warning("Fallback API distante indisponible: %s", exc)
      return []

    offers: list[dict] = []
    for job in jobs[:12]:
        title = f"Stage {job.get('title', '').strip()}".strip()
        description = BeautifulSoup(job.get("description", ""), "html.parser").get_text(" ", strip=True)
        location = "Remote Maroc"
        offers.append({
            "title": title,
            "description": description[:1800],
            "location": location,
            "company_name": job.get("company_name") or "Remote company",
            "source_url": job.get("url"),
            "source_platform": "Remote import",
            "published_date": date.today(),
            "offer_type": "stage",
            "duration_months": 4,
        })
    return offers


def _scraper_company_for_offer(offer_data: dict) -> CompanyProfile:
    raw_company = (
        offer_data.get("company_name")
        or offer_data.get("source_platform")
        or "Offres importees"
    )
    company_name = str(raw_company).strip()[:200] or "Offres importees"
    source = str(offer_data.get("source_platform") or "scraper").strip()
    digest = hashlib.sha1(f"{source}:{company_name}".encode("utf-8")).hexdigest()[:10]
    username = f"scraper_{_slug(company_name)}_{digest}"[:150]
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "role": "company",
            "email": f"{username}@scraper.local",
        },
    )
    if user.role != "company":
        user.role = "company"
        user.save(update_fields=["role"])
    profile, _ = CompanyProfile.objects.get_or_create(
        user=user,
        defaults={
            "company_name": company_name,
            "city": _detect_location(str(offer_data.get("location") or "")),
            "country": "Maroc" if _is_moroccan_offer(offer_data) else "Remote",
        },
    )
    if profile.company_name != company_name:
        profile.company_name = company_name
        profile.save(update_fields=["company_name"])
    return profile


def _upsert_scraped_offers(scraped_offers: Iterable[dict]) -> dict[str, int]:
    created_count = 0
    updated_count = 0
    skipped_count = 0
    for offer_data in scraped_offers:
        if not (_is_moroccan_offer(offer_data) or _looks_relevant_offer(offer_data)):
            skipped_count += 1
            continue

        source_url = offer_data.get("source_url")
        title = (offer_data.get("title") or "").strip()
        location = offer_data.get("location") or "Maroc"
        if not title:
            skipped_count += 1
            continue
        if source_url and InternshipOffer.objects.filter(source_url=source_url).count() > 1:
            InternshipOffer.objects.filter(source_url=source_url).order_by("id")[1:].update(
                status=InternshipOffer.Status.ARCHIVED
            )

        description = (offer_data.get("description") or "")[:2500]
        required_skills = (offer_data.get("required_skills") or "").strip()
        if not required_skills:
            required_skills = skills_heuristic_string(description)
        offer_type = offer_data.get("offer_type") or _detect_offer_type(offer_data)
        duration = offer_data.get("duration_months")
        is_paid = bool(offer_data.get("is_paid", False))
        salary = offer_data.get("salary") if is_paid else None
        company = _scraper_company_for_offer(offer_data)
        lookup = {"company": company, "title": title, "location": location}
        if source_url:
            lookup = {"source_url": source_url}

        offer, created = InternshipOffer.objects.update_or_create(
            defaults={
                "title": title,
                "company": company,
                "description": description,
                "required_skills": required_skills,
                "offer_type": offer_type,
                "location": location,
                "duration_months": duration if offer_type == "stage" else duration,
                "status": InternshipOffer.Status.ACTIVE,
                "source_url": source_url,
                "source_platform": offer_data.get("source_platform", "Scraper Maroc"),
                "published_date": offer_data.get("published_date") or date.today(),
                "contact_email": offer_data.get("contact_email"),
                "is_paid": is_paid,
                "salary": salary,
            },
            **lookup,
        )
        if created:
            created_count += 1
        else:
            updated_count += 1

    return {
        "created": created_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "total_seen": created_count + updated_count + skipped_count,
    }


def fetch_moroccan_internships(
    *,
    use_scraper_ai: bool = True,
    scraper_ai_chunk_size: int | None = None,
) -> dict[str, int]:
    """
    Agrège plusieurs sources orientées Maroc.
    Si le scraping réel ne remonte rien, on injecte un lot cohérent d'offres Maroc.

    use_scraper_ai: enrichissement Gemini par lots (sinon heuristique NLP seule).
    scraper_ai_chunk_size: nombre d'offres par appel Gemini (defaut: env GEMINI_SCRAPER_CHUNK ou 8).
    """
    logger.info("Demarrage du scraping des offres Maroc.")

    scraped_offers: list[dict] = []
    terms = DEFAULT_SEARCH_TERMS
    for term in terms:
        scraped_offers.extend(_parse_rekrute(term))
        scraped_offers.extend(_parse_emploi_ma(term))
    scraped_offers.extend(_build_remote_morocco_offers())
    scraped_offers.extend(_parse_arbeitnow())
    scraped_offers.extend(_parse_remoteok())

    if not scraped_offers and os.getenv("SCRAPER_USE_DEMO_FALLBACK", "").lower() in {"1", "true", "yes"}:
        scraped_offers = DEFAULT_MOROCCAN_OFFERS

    normalized_offers = []
    seen_urls: set[str] = set()
    seen_fingerprints: set[str] = set()
    for offer in scraped_offers:
        source_url = offer.get("source_url")
        title = offer.get("title", "").strip()
        location = offer.get("location") or _detect_location(
            f"{offer.get('title', '')} {offer.get('description', '')}"
        )
        fingerprint = f"{_normalize_text(title)}|{_normalize_text(location)}|{_normalize_text(offer.get('company_name', ''))}"
        if source_url and source_url in seen_urls:
            continue
        if not source_url and fingerprint in seen_fingerprints:
            continue
        if source_url:
            seen_urls.add(source_url)
        seen_fingerprints.add(fingerprint)
        normalized_offers.append({
            "title": title,
            "description": offer.get("description", "").strip(),
            "location": location,
            "company_name": offer.get("company_name"),
            "offer_type": offer.get("offer_type") or _detect_offer_type(offer),
            "duration_months": offer.get("duration_months", 4 if offer.get("offer_type") == "stage" else None),
            "source_url": source_url,
            "source_platform": offer.get("source_platform", "Scraper Maroc"),
            "published_date": offer.get("published_date") or date.today(),
            "contact_email": offer.get("contact_email"),
            "is_paid": offer.get("is_paid", False),
            "salary": offer.get("salary"),
        })

    ai_stats = enrich_scraped_offers_with_ai(
        normalized_offers,
        use_ai=use_scraper_ai,
        chunk_size=scraper_ai_chunk_size,
    )
    stats = _upsert_scraped_offers(normalized_offers)
    stats.update(ai_stats)
    logger.info(
        "Scraping Maroc termine. %s creees, %s mises a jour, %s ignorees. "
        "IA lots: %s batches, %s enrichies IA, heuristique seule: %s, lots IA en echec: %s.",
        stats["created"],
        stats["updated"],
        stats["skipped"],
        ai_stats.get("ai_batches", 0),
        ai_stats.get("offers_ai_enriched", 0),
        ai_stats.get("offers_heuristic_only", 0),
        ai_stats.get("ai_chunks_failed", 0),
    )
    return stats
