"""
ai/views.py - API views for recommendations and AI helpers
"""

import logging

from core.gemini import configure_gemini_client, gemini_model_name
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Recommendation
from .serializers import RecommendationSerializer
from .services import NLPService
from .throttles import GeminiUserThrottle
from users.views import IsStudent

logger = logging.getLogger(__name__)

INTERVIEW_HISTORY_MAX = 24


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        from django.db.models import Q

        student = self.request.user.student_profile
        top_n = int(self.request.query_params.get("top", 20))
        top_n = min(top_n, 50)
        location = self.request.query_params.get("location", "").strip()
        offer_type = self.request.query_params.get("type", "").strip()

        queryset = Recommendation.objects.filter(
            student=student,
            offer__status="active",
            score__gt=0,
        )

        if location:
            queryset = queryset.filter(
                Q(offer__company__city__icontains=location)
                | Q(offer__company__country__icontains=location)
                | Q(offer__location__icontains=location)
            )

        if offer_type:
            queryset = queryset.filter(offer__offer_type=offer_type)

        return queryset.select_related("offer__company__user").order_by("-score")[:top_n]

    def list(self, request, *args, **kwargs):
        student = request.user.student_profile
        nlp = NLPService()

        if not student.cv_file:
            return Response(
                {
                    "detail": "Uploadez votre CV pour obtenir des recommandations.",
                    "recommendations": [],
                    "cv_uploaded": False,
                },
                status=status.HTTP_200_OK,
            )

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                "cv_uploaded": True,
                "extracted_profile": {
                    "skills": student.extracted_skills or [],
                    "experience_level": student.experience_level or "Non specifie",
                    "projects": student.projects or [],
                    "target_job_titles": student.target_job_titles or [],
                    "preferred_locations": student.preferred_locations or [],
                    "preferred_offer_types": student.preferred_offer_types or [],
                    "remote_ok": student.remote_ok,
                    "expected_salary": student.expected_salary,
                },
                "career_insights": nlp.build_career_insights(student, queryset),
                "recommendations_count": len(serializer.data),
                "recommendations": serializer.data,
            }
        )


class RefreshRecommendationsView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        student = request.user.student_profile

        if not student.cv_file:
            return Response(
                {"detail": "Vous devez d'abord uploader votre CV."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            nlp = NLPService()
            count = nlp.process_student_cv(student)
            return Response(
                {
                    "message": "Recommandations recalculees avec succes.",
                    "offers_analyzed": count,
                }
            )
        except Exception:
            logger.exception("Echec recalcul recommandations.")
            return Response(
                {"detail": "Erreur lors du calcul des recommandations."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AIStatsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.db.models import Avg, Count, Max
        from offers.models import InternshipOffer
        from users.models import StudentProfile

        stats = Recommendation.objects.aggregate(
            total=Count("id"),
            avg_score=Avg("score"),
            max_score=Max("score"),
        )
        stats.update(
            {
                "total_offers": InternshipOffer.objects.filter(status="active").count(),
                "total_students": StudentProfile.objects.filter(cv_file__isnull=False).count(),
                "students_with_preferences": StudentProfile.objects.exclude(target_job_titles=[]).count(),
            }
        )
        return Response(stats)


class GenerateCoverLetterView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [GeminiUserThrottle]

    def post(self, request, offer_id):
        from offers.models import InternshipOffer

        student = request.user.student_profile

        if not student.cv_text_extracted:
            return Response(
                {"detail": "Votre CV n'a pas encore ete scanne. Uploadez votre CV d'abord."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            offer = InternshipOffer.objects.get(id=offer_id, status="active")
        except InternshipOffer.DoesNotExist:
            return Response({"detail": "Offre introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not configure_gemini_client():
            return Response({"detail": "Cle API IA manquante."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            import google.generativeai as genai

            model = genai.GenerativeModel(gemini_model_name())

            student_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            student_skills = ", ".join(student.extracted_skills or [])

            prompt = f"""
            Tu es un expert en redaction de lettres de motivation professionnelles en francais.
            Redige une lettre de motivation convaincante, elegante et personnalisee pour le candidat ci-dessous.

            CANDIDAT :
            - Nom : {student_name}
            - Competences cles : {student_skills}
            - Resume du profil (extrait du CV) : {student.cv_text_extracted[:800]}

            OFFRE DE STAGE CIBLEE :
            - Titre : {offer.title}
            - Entreprise : {offer.company.company_name}
            - Ville : {offer.company.city or "Non precisee"}
            - Competences requises : {offer.required_skills}
            - Description du poste : {offer.description[:500]}

            CONSIGNES :
            - Commence directement par "Madame, Monsieur,"
            - Structure : accroche personnalisee -> motivation pour l'entreprise -> valeur ajoutee du candidat -> conclusion
            - Longueur : 3 a 4 paragraphes, environ 250 mots
            - Ton : professionnel, enthousiaste, confiant
            - Ne mets pas de titre, de date ou d'adresse en haut
            """

            response = model.generate_content(prompt)
            return Response(
                {
                    "offer_title": offer.title,
                    "company_name": offer.company.company_name,
                    "cover_letter": response.text.strip(),
                }
            )
        except Exception:
            logger.exception("Echec generation lettre Gemini.")
            return Response(
                {"detail": "Erreur lors de la generation de la lettre. Reessayez plus tard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InterviewBotView(APIView):
    permission_classes = [IsStudent]
    throttle_classes = [GeminiUserThrottle]

    def post(self, request, offer_id):
        from offers.models import InternshipOffer

        student_message = (request.data.get("message") or "")[:4000]
        history = request.data.get("history") or []
        if isinstance(history, list) and len(history) > INTERVIEW_HISTORY_MAX:
            history = history[-INTERVIEW_HISTORY_MAX:]

        try:
            offer = InternshipOffer.objects.get(id=offer_id, status="active")
        except InternshipOffer.DoesNotExist:
            return Response({"detail": "Offre introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if not configure_gemini_client():
            return Response({"detail": "Cle API IA manquante."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            import google.generativeai as genai

            model = genai.GenerativeModel(gemini_model_name())

            system_context = f"""
            Tu es un recruteur technique senior chez '{offer.company.company_name}'.
            Tu fais passer un entretien de stage pour le poste : '{offer.title}'.
            Competences requises pour ce poste : {offer.required_skills}.

            Regles strictes :
            - Pose une seule question technique a la fois.
            - Apres la reponse de l'etudiant, donne un feedback court puis pose la prochaine question.
            - Varie les types de questions : theorie, cas pratiques, problemes de code.
            - Si c'est le premier message de l'etudiant, commence par te presenter et poser la premiere question.
            - Reste professionnel et bienveillant.
            - Reponds toujours en francais.
            """

            conversation_parts = [system_context, "\n\nDebut de l'entretien:\n"]
            for msg in history:
                if not isinstance(msg, dict):
                    continue
                text = (msg.get("text") or "")[:2000]
                role = "Recruteur" if msg.get("role") == "bot" else "Candidat"
                conversation_parts.append(f"{role}: {text}")

            if student_message:
                conversation_parts.append(f"Candidat: {student_message}")

            conversation_parts.append("Recruteur:")
            response = model.generate_content("\n".join(conversation_parts))

            return Response({"bot_message": response.text.strip(), "offer_title": offer.title})
        except Exception:
            logger.exception("Echec bot entretien Gemini.")
            return Response(
                {"detail": "Erreur lors de la simulation d'entretien. Reessayez plus tard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MarketTrendsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from collections import Counter
        from offers.models import InternshipOffer

        active_offers = list(
            InternshipOffer.objects.filter(status="active").values(
                "required_skills",
                "location",
                "source_platform",
            )
        )
        nlp = NLPService()
        skill_counter = Counter()
        city_counter = Counter()
        platform_counter = Counter()

        for offer in active_offers:
            for skill in nlp.split_skill_string(offer.get("required_skills")):
                if skill and len(skill) > 1:
                    skill_counter[skill.title()] += 1

            if offer.get("location"):
                city_counter[str(offer["location"]).title()] += 1
            if offer.get("source_platform"):
                platform_counter[str(offer["source_platform"]).title()] += 1

        top_skills = [
            {
                "skill": skill,
                "count": count,
                "percentage": round(count / max(len(active_offers), 1) * 100, 1),
            }
            for skill, count in skill_counter.most_common(15)
        ]

        return Response(
            {
                "total_offers_analyzed": len(active_offers),
                "top_skills": top_skills,
                "top_cities": [{"city": city, "count": count} for city, count in city_counter.most_common(8)],
                "top_platforms": [
                    {"platform": platform, "count": count}
                    for platform, count in platform_counter.most_common(6)
                ],
            }
        )
