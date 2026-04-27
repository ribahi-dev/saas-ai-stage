"""
ai/urls.py — Routes du moteur de recommandation & IA

  GET  /api/ai/recommendations/             → Mes recommandations (étudiant)
  POST /api/ai/recommendations/refresh/     → Recalculer mes scores
  GET  /api/ai/stats/                       → Statistiques (admin)
  POST /api/ai/cover-letter/<id>/           → Générer une lettre de motivation IA
  POST /api/ai/interview/<id>/              → Simulateur d'entretien IA
  GET  /api/ai/market-trends/               → Tendances du marché
"""

from django.urls import path
from .views import (
    RecommendationListView, RefreshRecommendationsView, AIStatsView,
    GenerateCoverLetterView, InterviewBotView, MarketTrendsView
)

urlpatterns = [
    path('recommendations/',                 RecommendationListView.as_view(),       name='recommendations'),
    path('recommendations/refresh/',         RefreshRecommendationsView.as_view(),   name='recommendations-refresh'),
    path('stats/',                           AIStatsView.as_view(),                  name='ai-stats'),
    path('cover-letter/<int:offer_id>/',     GenerateCoverLetterView.as_view(),      name='cover-letter'),
    path('interview/<int:offer_id>/',        InterviewBotView.as_view(),             name='interview-bot'),
    path('market-trends/',                   MarketTrendsView.as_view(),             name='market-trends'),
]
