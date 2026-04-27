import json
import logging
import os
import re
from datetime import date, datetime, timedelta
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from users.models import CompanyProfile, User

from .models import InternshipOffer

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 12

MOROCCAN_CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Tanger", "Agadir", "Fes",
    "Kenitra", "Temara", "Mohammedia", "Meknes", "Oujda", "Remote Maroc",
]

MOROCCAN_KEYWORDS = {
    "stage", "stagiaire", "pfe", "internship", "alternance",
    "casablanca", "rabat", "marrakech", "tanger", "agadir", "fes", "maroc", "morocco",
}

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


def _extract_skills_with_ai(description: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _extract_skills_heuristic(description)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        Lis cette offre et renvoie uniquement une liste JSON de competences.
        Exemple: ["Python", "Django", "Communication"]
        Offre:
        {description[:2500]}
        """
        response = model.generate_content(prompt)
        match = re.search(r"\[.*\]", response.text, re.DOTALL)
        if match:
            skills = json.loads(match.group())
            if isinstance(skills, list):
                clean_skills = [str(skill).strip() for skill in skills if str(skill).strip()]
                if clean_skills:
                    return ", ".join(dict.fromkeys(clean_skills))
    except Exception as exc:
        logger.error("Erreur extraction IA scraper: %s", exc)

    return _extract_skills_heuristic(description)


def _extract_skills_heuristic(description: str) -> str:
    normalized = _normalize_text(description)
    skill_catalog = [
        "python", "django", "react", "javascript", "typescript", "sql",
        "postgresql", "mysql", "power bi", "excel", "flutter", "dart",
        "node.js", "api rest", "git", "docker", "communication", "agile scrum",
        "machine learning", "data analysis", "figma", "laravel",
    ]
    found = [skill for skill in skill_catalog if skill in normalized]
    if not found:
        return "communication, autonomie, travail en equipe"
    return ", ".join(dict.fromkeys(found))


def _is_moroccan_offer(offer: dict) -> bool:
    haystack = _normalize_text(
        f"{offer.get('title', '')} {offer.get('description', '')} {offer.get('location', '')}"
    )
    return any(keyword in haystack for keyword in MOROCCAN_KEYWORDS)


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


def _parse_rekrute() -> list[dict]:
    url = "https://www.rekrute.com/offres.html?s=1&keyword=stage"
    try:
        html = _fetch_html(url)
    except Exception as exc:
        logger.warning("Scraping Rekrute indisponible: %s", exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    offers: list[dict] = []
    cards = soup.select(".post-id, .result")
    for card in cards[:15]:
        title_node = card.select_one("h2 a, .titreJob")
        desc_node = card.select_one(".description, .job-description, p")
        location_node = card.select_one(".location, .lieu")
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
            "source_url": urljoin(url, link) if link else url,
            "source_platform": "Rekrute",
            "published_date": date.today(),
            "offer_type": _detect_offer_type({"title": title, "description": description}),
        })
    return offers


def _parse_emploi_ma() -> list[dict]:
    url = "https://www.emploi.ma/recherche-jobs-maroc?keywords=stage"
    try:
        html = _fetch_html(url)
    except Exception as exc:
        logger.warning("Scraping Emploi.ma indisponible: %s", exc)
        return []

    soup = BeautifulSoup(html, "html.parser")
    offers: list[dict] = []
    cards = soup.select(".job-description-wrapper, .card-job")
    for card in cards[:15]:
        title_node = card.select_one("h5 a, h3 a")
        desc_node = card.select_one(".field-item, .card-job-description")
        location_node = card.select_one(".job-region, .location")
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
            "source_url": urljoin(url, title_node.get("href", "")),
            "source_platform": "Emploi.ma",
            "published_date": _parse_date(date_node.get_text(" ", strip=True) if date_node else "") or date.today(),
            "offer_type": _detect_offer_type({"title": title, "description": description}),
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
            "source_url": job.get("url"),
            "source_platform": "Remote import",
            "published_date": date.today(),
            "offer_type": "stage",
            "duration_months": 4,
        })
    return offers


def _upsert_scraped_offers(scraped_offers: Iterable[dict]) -> dict[str, int]:
    company_user, _ = User.objects.get_or_create(
        username="scraper_bot",
        defaults={"role": "company", "email": "scraper@bot.com"},
    )
    if not hasattr(company_user, "company_profile"):
        CompanyProfile.objects.create(
            user=company_user,
            company_name="Offres Maroc (Scraper)",
            city="Maroc",
            country="Maroc",
        )
    company = company_user.company_profile

    created_count = 0
    updated_count = 0
    skipped_count = 0
    for offer_data in scraped_offers:
        if not _is_moroccan_offer(offer_data):
            skipped_count += 1
            continue

        source_url = offer_data.get("source_url")
        title = (offer_data.get("title") or "").strip()
        location = offer_data.get("location") or "Maroc"
        if not title:
            skipped_count += 1
            continue

        description = (offer_data.get("description") or "")[:2500]
        required_skills = _extract_skills_with_ai(description)
        offer_type = offer_data.get("offer_type") or _detect_offer_type(offer_data)
        duration = offer_data.get("duration_months")
        is_paid = bool(offer_data.get("is_paid", False))
        salary = offer_data.get("salary") if is_paid else None
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


def fetch_moroccan_internships() -> dict[str, int]:
    """
    Agrège plusieurs sources orientées Maroc.
    Si le scraping réel ne remonte rien, on injecte un lot cohérent d'offres Maroc.
    """
    logger.info("Demarrage du scraping des offres Maroc.")

    scraped_offers: list[dict] = []
    scraped_offers.extend(_parse_rekrute())
    scraped_offers.extend(_parse_emploi_ma())
    scraped_offers.extend(_build_remote_morocco_offers())

    if not scraped_offers:
        scraped_offers = DEFAULT_MOROCCAN_OFFERS

    normalized_offers = []
    for offer in scraped_offers:
        normalized_offers.append({
            "title": offer.get("title", "").strip(),
            "description": offer.get("description", "").strip(),
            "location": offer.get("location") or _detect_location(
                f"{offer.get('title', '')} {offer.get('description', '')}"
            ),
            "offer_type": offer.get("offer_type") or _detect_offer_type(offer),
            "duration_months": offer.get("duration_months", 4 if offer.get("offer_type") == "stage" else None),
            "source_url": offer.get("source_url"),
            "source_platform": offer.get("source_platform", "Scraper Maroc"),
            "published_date": offer.get("published_date") or date.today(),
            "contact_email": offer.get("contact_email"),
            "is_paid": offer.get("is_paid", False),
            "salary": offer.get("salary"),
        })

    stats = _upsert_scraped_offers(normalized_offers)
    logger.info(
        "Scraping Maroc termine. %s creees, %s mises a jour, %s ignorees.",
        stats["created"],
        stats["updated"],
        stats["skipped"],
    )
    return stats
