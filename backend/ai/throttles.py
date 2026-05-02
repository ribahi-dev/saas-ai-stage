"""Limitation de debit pour les endpoints consommateurs de Gemini."""

from rest_framework.throttling import UserRateThrottle


class GeminiUserThrottle(UserRateThrottle):
    """Quota horaire par utilisateur authentifie sur lettre / entretien IA."""

    scope = "gemini_user"
