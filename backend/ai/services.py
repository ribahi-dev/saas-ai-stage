"""
ai/services.py - Moteur de recommandation de stages

Objectifs:
  - Extraire un profil exploitable depuis le CV
  - Normaliser les competences cote CV et cote offre
  - Calculer un score hybride:
      * similarite TF-IDF
      * overlap de competences
      * bonus contexte (stage, Maroc, etc.)
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections import Counter
from typing import Iterable

import pdfplumber

try:
    import docx
except ImportError:  # pragma: no cover - optionnel
    docx = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class NLPService:
    VECTORIZER_PARAMS = {
        "max_features": 5000,
        "ngram_range": (1, 2),
        "sublinear_tf": True,
        "min_df": 1,
    }

    SKILL_ALIASES = {
        "js": "javascript",
        "ts": "typescript",
        "node": "node.js",
        "nodejs": "node.js",
        "node.js": "node.js",
        "reactjs": "react",
        "nextjs": "next.js",
        "next": "next.js",
        "vuejs": "vue",
        "postgres": "postgresql",
        "postgre": "postgresql",
        "postgresql": "postgresql",
        "ml": "machine learning",
        "ai": "intelligence artificielle",
        "nlp": "traitement du langage naturel",
        "rest": "api rest",
        "restful": "api rest",
        "dockerization": "docker",
        "k8s": "kubernetes",
        "ci/cd": "ci cd",
        "scrum": "agile scrum",
    }

    SKILL_PATTERNS = [
        "python", "django", "flask", "fastapi", "java", "spring", "php", "laravel",
        "javascript", "typescript", "react", "next.js", "vue", "angular",
        "node.js", "express", "nestjs", "html", "css", "tailwind", "bootstrap",
        "sql", "mysql", "postgresql", "mongodb", "redis", "firebase",
        "docker", "kubernetes", "git", "github", "gitlab", "linux",
        "aws", "azure", "gcp", "power bi", "excel", "tableau",
        "pandas", "numpy", "scikit-learn", "machine learning", "deep learning",
        "tensorflow", "pytorch", "nlp", "data analysis", "data engineering",
        "api rest", "graphql", "testing", "pytest", "selenium",
        "agile scrum", "communication", "problem solving", "leadership",
        "francais", "anglais", "arabic",
    ]

    MOROCCAN_CITIES = {
        "casablanca", "rabat", "sale", "kenitra", "fes", "meknes", "marrakech",
        "agadir", "tanger", "tetouan", "oujda", "el jadida", "mohammedia",
        "beni mellal", "nador", "safi", "temara", "khouribga",
    }

    EXPERIENCE_HINTS = {
        "Stage": ["stage", "pfe", "pfa", "fin d'etudes", "fin etudes", "internship"],
        "Junior": ["junior", "debutant", "0 an", "0-1 an"],
        "Intermediaire": ["1 an", "2 ans", "alternance", "freelance"],
        "Confirme": ["3 ans", "4 ans", "5 ans", "senior", "lead"],
    }
    TRACK_KEYWORDS = {
        "software_engineering": ["python", "django", "react", "javascript", "api", "full stack", "backend", "frontend"],
        "data_ai": ["data", "power bi", "machine learning", "pandas", "sql", "tableau", "analysis"],
        "mobile": ["flutter", "dart", "android", "ios", "mobile"],
        "product_design": ["figma", "ux", "ui", "design", "prototype"],
    }

    def __init__(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn n'est pas installe.")
        self.vectorizer = TfidfVectorizer(**self.VECTORIZER_PARAMS)

    def normalize_text(self, text: str) -> str:
        text = (text or "").lower()
        text = re.sub(r"[^\w\s\+\#\.\-\/]", " ", text)
        text = text.replace("c sharp", "c#").replace("c plus plus", "c++")
        return " ".join(text.split())

    def canonicalize_skill(self, skill: str) -> str:
        normalized = self.normalize_text(skill)
        return self.SKILL_ALIASES.get(normalized, normalized)

    def split_skill_string(self, skills: str | Iterable[str] | None) -> list[str]:
        if skills is None:
            return []
        if isinstance(skills, str):
            items = re.split(r"[,;/\n]", skills)
        else:
            items = list(skills)

        normalized_skills: list[str] = []
        seen: set[str] = set()
        for item in items:
            canonical = self.canonicalize_skill(str(item))
            if canonical and canonical not in seen:
                normalized_skills.append(canonical)
                seen.add(canonical)
        return normalized_skills

    def normalize_list_text(self, values: Iterable[str] | None) -> list[str]:
        if not values:
            return []
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = self.normalize_text(str(value))
            if item and item not in seen:
                normalized.append(item)
                seen.add(item)
        return normalized

    def extract_text_from_cv(self, file_path: str) -> str:
        text_parts: list[str] = []
        try:
            if file_path.lower().endswith((".docx", ".doc")):
                if docx is None:
                    logger.warning("python-docx indisponible pour lire %s", file_path)
                    return ""
                document = docx.Document(file_path)
                for paragraph in document.paragraphs:
                    if paragraph.text:
                        text_parts.append(paragraph.text)
            else:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
        except Exception as exc:  # pragma: no cover - dependant fichier
            logger.error("Erreur extraction CV (%s): %s", file_path, exc)
            return ""

        return self.normalize_text(" ".join(text_parts))

    def extract_skills_from_text(self, text: str) -> list[str]:
        normalized = self.normalize_text(text)
        found_skills: list[str] = []

        for pattern in self.SKILL_PATTERNS:
            if pattern in normalized:
                found_skills.append(self.canonicalize_skill(pattern))

        # Extrait aussi les tokens techniques "propres"
        raw_tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9\.\+\#\-]{1,24}", normalized)
        for token in raw_tokens:
            canonical = self.canonicalize_skill(token)
            if canonical in self.SKILL_PATTERNS or canonical in self.SKILL_ALIASES.values():
                found_skills.append(canonical)

        deduped: list[str] = []
        seen: set[str] = set()
        for skill in found_skills:
            if skill and skill not in seen:
                deduped.append(skill)
                seen.add(skill)
        return deduped

    def extract_profile_with_ai(self, cv_text: str) -> dict[str, object]:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            heuristic_skills = self.extract_skills_from_text(cv_text)
            return {
                "skills": heuristic_skills,
                "experience_level": self.estimate_experience_level(cv_text),
                "projects": self.extract_project_lines(cv_text),
            }

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            Analyse ce CV d'etudiant et retourne uniquement un JSON valide.
            Format attendu:
            {{
              "skills": ["skill1", "skill2"],
              "experience_level": "Junior|Stage|Confirme",
              "projects": ["projet 1", "projet 2"]
            }}
            CV:
            {cv_text[:3500]}
            """
            response = model.generate_content(prompt)
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if not match:
                raise ValueError("JSON introuvable dans la reponse IA")
            data = json.loads(match.group())
            skills = [
                self.canonicalize_skill(skill)
                for skill in data.get("skills", [])
                if isinstance(skill, str)
            ]
            return {
                "skills": list(dict.fromkeys(skills)),
                "experience_level": data.get("experience_level") or self.estimate_experience_level(cv_text),
                "projects": data.get("projects") or self.extract_project_lines(cv_text),
            }
        except Exception as exc:
            logger.error("Erreur IA Gemini sur le CV: %s", exc)
            heuristic_skills = self.extract_skills_from_text(cv_text)
            return {
                "skills": heuristic_skills,
                "experience_level": self.estimate_experience_level(cv_text),
                "projects": self.extract_project_lines(cv_text),
            }

    def estimate_experience_level(self, cv_text: str) -> str:
        text = self.normalize_text(cv_text)
        for label, tokens in self.EXPERIENCE_HINTS.items():
            if any(token in text for token in tokens):
                return label
        return "Junior"

    def extract_project_lines(self, cv_text: str) -> list[str]:
        parts = re.split(r"[;\n\.]", cv_text)
        projects = []
        for part in parts:
            cleaned = " ".join(part.split())
            if 12 <= len(cleaned) <= 120 and any(
                keyword in cleaned
                for keyword in ["projet", "application", "dashboard", "site web", "api", "plateforme"]
            ):
                projects.append(cleaned[:120])
        return projects[:4]

    def build_offer_text(self, offer) -> str:
        chunks = [
            offer.title or "",
            offer.required_skills or "",
            offer.description[:800] if offer.description else "",
            offer.location or "",
            offer.company.company_name if getattr(offer, "company", None) else "",
            offer.company.city if getattr(offer.company, "city", None) else "",
        ]
        return self.normalize_text(" ".join(chunk for chunk in chunks if chunk))

    def compute_similarity(self, cv_text: str, offer_texts: list[str]) -> list[float]:
        if not cv_text or not offer_texts:
            return [0.0] * len(offer_texts)

        corpus = [cv_text] + offer_texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
        except Exception as exc:
            logger.error("Erreur TF-IDF: %s", exc)
            return [0.0] * len(offer_texts)

        cv_vector = tfidf_matrix[0:1]
        offer_vectors = tfidf_matrix[1:]
        similarities = cosine_similarity(cv_vector, offer_vectors).flatten()
        return similarities.tolist()

    def compute_skill_overlap(self, student_skills: Iterable[str], offer_skills: Iterable[str]) -> float:
        student_set = {self.canonicalize_skill(skill) for skill in student_skills if skill}
        offer_set = {self.canonicalize_skill(skill) for skill in offer_skills if skill}
        if not offer_set:
            return 0.0
        overlap = len(student_set.intersection(offer_set))
        return overlap / max(len(offer_set), 1)

    def compute_context_bonus(self, student_profile, offer) -> float:
        bonus = 0.0
        if offer.offer_type == "stage":
            bonus += 0.05
        if offer.location and any(city in self.normalize_text(offer.location) for city in self.MOROCCAN_CITIES):
            bonus += 0.03
        if student_profile.experience_level == "Junior" and offer.offer_type == "stage":
            bonus += 0.04
        if offer.is_paid:
            bonus += 0.02
        if getattr(offer.company, "country", "") and "maroc" in self.normalize_text(offer.company.country):
            bonus += 0.02
        return min(bonus, 0.1)

    def compute_preference_bonus(self, student_profile, offer, offer_text: str) -> float:
        bonus = 0.0
        normalized_location = self.normalize_text(offer.location or "")
        preferred_locations = self.normalize_list_text(getattr(student_profile, "preferred_locations", []))
        target_job_titles = self.normalize_list_text(getattr(student_profile, "target_job_titles", []))
        preferred_offer_types = set(self.normalize_list_text(getattr(student_profile, "preferred_offer_types", [])))
        expected_salary = getattr(student_profile, "expected_salary", None)

        if preferred_locations and any(location in normalized_location for location in preferred_locations):
            bonus += 0.06

        if target_job_titles and any(title in offer_text for title in target_job_titles):
            bonus += 0.07

        if preferred_offer_types and self.normalize_text(offer.offer_type) in preferred_offer_types:
            bonus += 0.05

        if getattr(student_profile, "remote_ok", True) and "remote" in normalized_location:
            bonus += 0.03

        if expected_salary and offer.salary and offer.salary >= expected_salary:
            bonus += 0.03

        return min(bonus, 0.12)

    def blend_score(self, semantic_score: float, skill_overlap: float, context_bonus: float) -> float:
        blended = (semantic_score * 0.65) + (skill_overlap * 0.30) + context_bonus
        return max(0.0, min(round(blended, 4), 1.0))

    def summarize_recommendation(
        self,
        student_skills: Iterable[str],
        offer_skills: Iterable[str],
        offer,
        final_score: float,
    ) -> str:
        student_set = set(self.split_skill_string(student_skills))
        offer_set = self.split_skill_string(offer_skills)
        matching = [skill for skill in offer_set if skill in student_set][:3]
        missing = [skill for skill in offer_set if skill not in student_set][:2]

        parts: list[str] = []
        if final_score >= 0.8:
            parts.append("Tres forte correspondance")
        elif final_score >= 0.6:
            parts.append("Bonne correspondance")
        else:
            parts.append("Correspondance interessante")

        if matching:
            parts.append(f"grace a {', '.join(matching)}")
        if getattr(offer, "location", None):
            parts.append(f"pour {offer.location}")
        if missing:
            parts.append(f"axes a renforcer: {', '.join(missing)}")
        return ". ".join(parts) + "."

    def derive_track(self, skills: Iterable[str]) -> str:
        skill_text = " ".join(self.normalize_list_text(skills))
        scores = {
            track: sum(1 for keyword in keywords if keyword in skill_text)
            for track, keywords in self.TRACK_KEYWORDS.items()
        }
        best_track, best_score = max(scores.items(), key=lambda item: item[1], default=("generaliste", 0))
        if best_score == 0:
            return "generaliste"
        return best_track

    def build_recommendation_insights(
        self,
        student_profile,
        offer,
        semantic_score: float,
        overlap_score: float,
        context_bonus: float,
        preference_bonus: float,
        final_score: float,
        matching_skills: list[str],
        missing_skills: list[str],
    ) -> dict[str, object]:
        return {
            "semantic_score": round(semantic_score * 100, 1),
            "skill_overlap_score": round(overlap_score * 100, 1),
            "context_bonus": round(context_bonus * 100, 1),
            "preference_bonus": round(preference_bonus * 100, 1),
            "matching_skills": matching_skills[:5],
            "missing_skills": missing_skills[:5],
            "score_band": (
                "excellent" if final_score >= 0.8
                else "fort" if final_score >= 0.65
                else "prometteur" if final_score >= 0.5
                else "a explorer"
            ),
            "recommendation_summary": self.summarize_recommendation(
                student_profile.extracted_skills or [],
                offer.required_skills or "",
                offer,
                final_score,
            ),
        }

    def build_career_insights(self, student_profile, recommendations) -> dict[str, object]:
        recommended_offers = list(recommendations)
        student_skills = self.split_skill_string(student_profile.extracted_skills or [])
        strengths = student_skills[:6]

        missing_counter: Counter[str] = Counter()
        cities_counter: Counter[str] = Counter()
        tracks_counter: Counter[str] = Counter()

        for recommendation in recommended_offers[:10]:
            insights = recommendation.insights or {}
            for skill in insights.get("missing_skills", []):
                missing_counter[str(skill)] += 1
            if recommendation.offer.location:
                cities_counter[str(recommendation.offer.location)] += 1
            offer_skills = self.split_skill_string(recommendation.offer.required_skills or "")
            tracks_counter[self.derive_track(offer_skills)] += 1

        target_track = tracks_counter.most_common(1)[0][0] if tracks_counter else self.derive_track(student_skills)
        completion_score = 40
        if student_profile.cv_file:
            completion_score += 20
        if student_profile.bio:
            completion_score += 10
        if student_profile.university and student_profile.field_of_study:
            completion_score += 10
        if student_profile.target_job_titles:
            completion_score += 10
        if student_profile.preferred_locations or student_profile.preferred_offer_types:
            completion_score += 10

        action_plan = []
        if not student_profile.target_job_titles:
            action_plan.append("Ajoutez 2 a 3 intitules cibles pour affiner vos recommandations.")
        if missing_counter:
            top_missing = [skill for skill, _ in missing_counter.most_common(3)]
            action_plan.append(f"Priorite apprentissage: {', '.join(top_missing)}.")
        if not student_profile.bio:
            action_plan.append("Renseignez une bio claire pour mieux presenter votre positionnement.")
        if not action_plan:
            action_plan.append("Votre profil est deja bien structure. Continuez a enrichir vos projets et competences.")

        return {
            "profile_completion_score": min(completion_score, 100),
            "strengths": strengths,
            "priority_skills": [skill for skill, _ in missing_counter.most_common(5)],
            "target_cities": [city for city, _ in cities_counter.most_common(5)],
            "recommended_track": target_track,
            "action_plan": action_plan,
        }

    def process_student_cv(self, student_profile) -> int:
        from ai.models import Recommendation
        from offers.models import InternshipOffer

        if not student_profile.cv_file:
            logger.warning("Aucun CV pour %s", student_profile.user.username)
            return 0

        cv_text = self.extract_text_from_cv(student_profile.cv_file.path)
        if not cv_text:
            logger.warning("CV vide ou illisible pour %s", student_profile.user.username)
            return 0

        profile = self.extract_profile_with_ai(cv_text)
        extracted_skills = profile.get("skills", []) if isinstance(profile, dict) else []
        experience_level = profile.get("experience_level", "Junior") if isinstance(profile, dict) else "Junior"
        projects = profile.get("projects", []) if isinstance(profile, dict) else []

        heuristic_skills = self.extract_skills_from_text(cv_text)
        merged_skills = list(dict.fromkeys([*heuristic_skills, *extracted_skills]))
        weighted_skill_text = " ".join(merged_skills * 3)
        enriched_cv_text = self.normalize_text(" ".join([cv_text, weighted_skill_text, " ".join(projects)]))

        student_profile.cv_text_extracted = enriched_cv_text
        student_profile.cv_vector_json = json.dumps(
            {
                "skills": merged_skills,
                "experience_level": str(experience_level),
                "projects": list(projects)[:4],
            }
        )
        student_profile.extracted_skills = merged_skills
        student_profile.experience_level = str(experience_level)
        student_profile.projects = list(projects)[:4]
        student_profile.save(
            update_fields=[
                "cv_text_extracted",
                "cv_vector_json",
                "extracted_skills",
                "experience_level",
                "projects",
            ]
        )

        active_offers = list(
            InternshipOffer.objects.filter(status="active").select_related("company")
        )
        if not active_offers:
            return 0

        offer_texts = [self.build_offer_text(offer) for offer in active_offers]
        semantic_scores = self.compute_similarity(enriched_cv_text, offer_texts)

        count = 0
        for offer, semantic_score, offer_text in zip(active_offers, semantic_scores, offer_texts):
            offer_skills = self.extract_skills_from_text(
                f"{offer.required_skills} {offer.description} {offer.title}"
            )
            overlap_score = self.compute_skill_overlap(merged_skills, offer_skills)
            context_bonus = self.compute_context_bonus(student_profile, offer)
            preference_bonus = self.compute_preference_bonus(student_profile, offer, offer_text)
            final_score = self.blend_score(semantic_score, overlap_score, context_bonus + preference_bonus)
            matching_skills = [skill for skill in offer_skills if skill in set(merged_skills)]
            missing_skills = [skill for skill in offer_skills if skill not in set(merged_skills)]

            skill_frequency = Counter(offer_skills)
            offer.offer_vector_json = json.dumps(
                {
                    "tokens": offer_skills,
                    "top_skills": [skill for skill, _ in skill_frequency.most_common(10)],
                    "normalized_text": offer_text[:1200],
                    "recommendation_summary": self.summarize_recommendation(merged_skills, offer_skills, offer, final_score),
                }
            )
            offer.save(update_fields=["offer_vector_json"])

            Recommendation.objects.update_or_create(
                student=student_profile,
                offer=offer,
                defaults={
                    "score": final_score,
                    "insights": self.build_recommendation_insights(
                        student_profile,
                        offer,
                        semantic_score,
                        overlap_score,
                        context_bonus,
                        preference_bonus,
                        final_score,
                        matching_skills,
                        missing_skills,
                    ),
                },
            )
            count += 1

        logger.info("[NLP] %s: %s recommandations calculees.", student_profile.user.username, count)
        return count

    def refresh_all_students(self) -> dict[str, int]:
        from users.models import StudentProfile

        processed = 0
        recommendations = 0
        students = StudentProfile.objects.filter(cv_file__isnull=False).select_related("user")

        for student in students:
            processed += 1
            recommendations += self.process_student_cv(student)

        return {
            "students_processed": processed,
            "recommendations_updated": recommendations,
        }

    def get_recommendations(self, student_profile, top_n: int = 10):
        from ai.models import Recommendation

        return (
            Recommendation.objects.filter(
                student=student_profile,
                offer__status="active",
                score__gt=0,
            )
            .select_related("offer__company")
            .order_by("-score")[:top_n]
        )
