"""
Enrichissement IA des offres scrapees (Gemini par lots).

Au lieu d'un appel Gemini par offre (cout et latence eleves), on envoie
plusieurs offres dans un seul prompt avec sortie JSON structuree, puis on
fusionne avec l'extraction heuristique (NLPService) pour aligner le matching CV.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from core.gemini import configure_gemini_client, gemini_model_name

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 8
MAX_DESC_PER_OFFER = 900
_RETRY_PAUSE_SEC = 2.0
_INTER_CHUNK_PAUSE_SEC = 1.0

_OFFER_TYPE_ALLOWED = frozenset({"stage", "emploi", "freelance"})


def _nlp():
    from ai.services import NLPService

    return NLPService()


def skills_heuristic_string(description: str) -> str:
    nlp = _nlp()
    skills = nlp.extract_skills_from_text(description or "")
    if not skills:
        return "communication, autonomie, travail en equipe"
    return ", ".join(skills)


def _merge_skill_lists(ai_skills: list[str], description: str, nlp) -> str:
    heuristic = nlp.extract_skills_from_text(description or "")
    merged: list[str] = []
    seen: set[str] = set()
    for raw in ai_skills + heuristic:
        if not raw or not isinstance(raw, str):
            continue
        s = nlp.canonicalize_skill(nlp.normalize_text(raw.strip()))
        if len(s) < 2 or s in seen:
            continue
        seen.add(s)
        merged.append(s)
    if not merged:
        return skills_heuristic_string(description)
    return ", ".join(merged)


def _parse_batch_json(text: str) -> list[dict[str, Any]]:
    text = (text or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[[\s\S]*\]", text)
        if not match:
            return []
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    return [x for x in data if isinstance(x, dict)]


def _call_gemini_batch(
    chunk: list[tuple[int, dict]],
    *,
    model,
) -> dict[int, dict[str, Any]]:
    """
    chunk: liste (index_global, offer_dict) avec title, description, offer_type deja detectes.
    Retourne index_global -> {skills, offer_type?, is_paid?, duration_months?}
    """
    lines = []
    for idx, offer in chunk:
        title = (offer.get("title") or "")[:200]
        desc = (offer.get("description") or "")[:MAX_DESC_PER_OFFER]
        ot = offer.get("offer_type") or "stage"
        lines.append(f'--- OFFRE index={idx} type_hint={ot} ---\nTitre: {title}\nDescription: {desc}\n')

    prompt = f"""Tu es un analyste RH tech specialise sur le marche marocain.
Pour CHAQUE offre ci-dessous (identifiee par index), extrais des metadonnees precises.

Regles:
- skills: 4 a 12 competences techniques ou soft skills pertinentes (francais ou anglais), sans doublons.
- offer_type: "stage" | "emploi" | "freelance" selon le contenu (stage/PFE/alternance -> stage).
- is_paid: true si remuneration / gratification / salaire mentionne pour un stage ou emploi.
- duration_months: entier 1-12 si une duree en mois est claire, sinon null.

Reponds UNIQUEMENT avec un JSON array, un objet par offre, dans le meme ordre que les blocs:
[{{"index": <int>, "skills": ["..."], "offer_type": "stage", "is_paid": false, "duration_months": null}}, ...]

Offres:
{"".join(lines)}
"""
    import google.generativeai as genai

    try:
        gen_cfg = genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.15,
            max_output_tokens=2048,
        )
        response = model.generate_content(prompt, generation_config=gen_cfg)
    except Exception:
        response = model.generate_content(prompt)
    raw = (response.text or "").strip()
    rows = _parse_batch_json(raw)
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        try:
            idx = int(row.get("index"))
        except (TypeError, ValueError):
            continue
        skills_raw = row.get("skills") or []
        if isinstance(skills_raw, str):
            skills_raw = [s.strip() for s in skills_raw.split(",") if s.strip()]
        if not isinstance(skills_raw, list):
            skills_raw = []
        skills_clean = [str(s).strip() for s in skills_raw if str(s).strip()][:20]

        ot = str(row.get("offer_type") or "").lower().strip()
        if ot not in _OFFER_TYPE_ALLOWED:
            ot = None

        is_paid = row.get("is_paid")
        if not isinstance(is_paid, bool):
            is_paid = None

        dur = row.get("duration_months")
        duration_months = None
        if dur is not None:
            try:
                d = int(dur)
                if 1 <= d <= 12:
                    duration_months = d
            except (TypeError, ValueError):
                pass

        out[idx] = {
            "skills": skills_clean,
            "offer_type": ot,
            "is_paid": is_paid,
            "duration_months": duration_months,
        }
    return out


def enrich_scraped_offers_with_ai(
    offers: list[dict],
    *,
    use_ai: bool = True,
    chunk_size: int | None = None,
) -> dict[str, int | float]:
    """
    Enrichit en place les dicts d'offres (cle required_skills, et optionnellement
    offer_type, is_paid, duration_months).

    Retourne des compteurs pour les logs / la commande management.
    """
    stats: dict[str, int | float] = {
        "ai_batches": 0,
        "ai_chunks_failed": 0,
        "offers_ai_enriched": 0,
        "offers_heuristic_only": 0,
    }
    if not offers:
        return stats

    nlp = _nlp()
    size = chunk_size or int(
        __import__("os").environ.get("GEMINI_SCRAPER_CHUNK", str(DEFAULT_CHUNK_SIZE))
    )
    size = max(2, min(size, 12))

    if not use_ai or not configure_gemini_client():
        for offer in offers:
            offer["required_skills"] = skills_heuristic_string(offer.get("description", ""))
            stats["offers_heuristic_only"] += 1
        return stats

    import google.generativeai as genai

    model = genai.GenerativeModel(gemini_model_name())
    indexed = list(enumerate(offers))

    for start in range(0, len(indexed), size):
        chunk = indexed[start : start + size]
        chunk_tuples = [(i, offers[i]) for i, _ in chunk]
        ai_by_index: dict[int, dict[str, Any]] = {}
        batch_ok = False
        for attempt in range(2):
            try:
                ai_by_index = _call_gemini_batch(chunk_tuples, model=model)
                batch_ok = True
                stats["ai_batches"] += 1
                break
            except Exception as exc:
                logger.warning(
                    "Batch Gemini scraper tentative %s/%s: %s",
                    attempt + 1,
                    2,
                    exc,
                )
                time.sleep(_RETRY_PAUSE_SEC)
        if not batch_ok:
            stats["ai_chunks_failed"] += 1

        for idx, offer in chunk_tuples:
            desc = offer.get("description") or ""
            ai_row = ai_by_index.get(idx)
            if ai_row and ai_row.get("skills"):
                offer["required_skills"] = _merge_skill_lists(ai_row["skills"], desc, nlp)
                stats["offers_ai_enriched"] += 1
                if ai_row.get("offer_type"):
                    offer["offer_type"] = ai_row["offer_type"]
                if ai_row.get("is_paid") is not None:
                    offer["is_paid"] = ai_row["is_paid"]
                if ai_row.get("duration_months") is not None:
                    offer["duration_months"] = ai_row["duration_months"]
            else:
                offer["required_skills"] = skills_heuristic_string(desc)
                stats["offers_heuristic_only"] += 1

        if start + size < len(indexed):
            time.sleep(_INTER_CHUNK_PAUSE_SEC)

    return stats
