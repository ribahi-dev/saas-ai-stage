"""
ai/serializers.py - Serialisation des recommandations
"""

import json

from rest_framework import serializers

from offers.serializers import InternshipOfferSerializer

from .models import Recommendation
from .services import NLPService


class RecommendationSerializer(serializers.ModelSerializer):
    offer_detail = InternshipOfferSerializer(source="offer", read_only=True)
    score_percent = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()
    matching_skills = serializers.SerializerMethodField()
    recommendation_summary = serializers.SerializerMethodField()
    insights = serializers.SerializerMethodField()

    _nlp_service = NLPService()

    class Meta:
        model = Recommendation
        fields = (
            "id",
            "offer",
            "offer_detail",
            "score",
            "score_percent",
            "matching_skills",
            "missing_skills",
            "recommendation_summary",
            "insights",
            "computed_at",
        )
        read_only_fields = fields

    def _student_skills(self, obj) -> set[str]:
        return set(self._nlp_service.split_skill_string(obj.student.extracted_skills or []))

    def _offer_skills(self, obj) -> list[str]:
        return self._nlp_service.split_skill_string(obj.offer.required_skills or "")

    def _offer_vector_payload(self, obj) -> dict:
        if not obj.offer.offer_vector_json:
            return {}
        try:
            return json.loads(obj.offer.offer_vector_json)
        except (TypeError, ValueError):
            return {}

    def get_score_percent(self, obj):
        return round(obj.score * 100, 1)

    def get_missing_skills(self, obj):
        student_skills = self._student_skills(obj)
        offer_skills = self._offer_skills(obj)
        return [
            skill for skill in offer_skills
            if skill.lower().strip() not in student_skills
        ][:4]

    def get_matching_skills(self, obj):
        student_skills = self._student_skills(obj)
        offer_skills = self._offer_skills(obj)
        return [
            skill for skill in offer_skills
            if skill.lower().strip() in student_skills
        ][:5]

    def get_recommendation_summary(self, obj):
        if obj.insights and obj.insights.get("recommendation_summary"):
            return obj.insights["recommendation_summary"]

        payload = self._offer_vector_payload(obj)
        if payload.get("recommendation_summary"):
            return payload["recommendation_summary"]

        matching = self.get_matching_skills(obj)
        missing = self.get_missing_skills(obj)

        if matching and missing:
            return (
                f"Bonne correspondance grace a {', '.join(matching[:3])}. "
                f"Competences a renforcer: {', '.join(missing[:2])}."
            )
        if matching:
            return f"Correspondance forte avec vos competences: {', '.join(matching[:3])}."
        if missing:
            return f"Offre interessante mais il manque surtout: {', '.join(missing[:3])}."
        return "Correspondance generale basee sur le contenu du CV et de l'offre."

    def get_insights(self, obj):
        return obj.insights or {}
