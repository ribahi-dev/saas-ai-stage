"""
offers/urls.py — Routes de l'app offers

  GET    /api/offers/                          → Liste publique (filtrée)
  POST   /api/offers/                          → Créer une offre (entreprise)
  GET    /api/offers/<id>/                     → Détail d'une offre
  PUT    /api/offers/<id>/                     → Modifier (entreprise propriétaire)
  PATCH  /api/offers/<id>/                     → Modifier partiellement
  DELETE /api/offers/<id>/                     → Supprimer
  POST   /api/offers/<id>/apply/               → Postuler (étudiant)
  GET    /api/offers/my-offers/                → Mes offres (entreprise)
  GET    /api/offers/my-applications/          → Mes candidatures (étudiant)
  GET    /api/offers/received-applications/    → Candidatures reçues (entreprise)
  PATCH  /api/offers/applications/<id>/status/ → Changer statut candidature
"""

from django.urls import path
from .views import (
    InternshipOfferListCreateView,
    InternshipOfferDetailView,
    ApplyToOfferView,
    MyOffersView,
    MyApplicationsView,
    WithdrawApplicationView,
    ReceivedApplicationsView,
    ApplicationStatusView,
    MoroccanOfferScrapeView,
)

urlpatterns = [
    # ── Offres ────────────────────────────────────────────────
    path('',                InternshipOfferListCreateView.as_view(), name='offer-list-create'),
    path('<int:pk>/',       InternshipOfferDetailView.as_view(),     name='offer-detail'),
    path('<int:pk>/apply/', ApplyToOfferView.as_view(),              name='offer-apply'),

    # ── Dashboard entreprise ──────────────────────────────────
    path('my-offers/',               MyOffersView.as_view(),            name='my-offers'),
    path('received-applications/',   ReceivedApplicationsView.as_view(), name='received-applications'),
    path('applications/<int:pk>/status/', ApplicationStatusView.as_view(), name='application-status'),
    path('scrape/morocco/', MoroccanOfferScrapeView.as_view(), name='scrape-morocco'),

    # ── Dashboard étudiant ────────────────────────────────────
    path('my-applications/', MyApplicationsView.as_view(), name='my-applications'),
    path('applications/<int:pk>/withdraw/', WithdrawApplicationView.as_view(), name='application-withdraw'),
]
