"""
offers/views.py — Vues API pour les Offres et Candidatures

Endpoints :
  GET    /api/offers/                    → Liste publique des offres actives
  POST   /api/offers/                    → Créer une offre (entreprise)
  GET    /api/offers/<id>/               → Détail d'une offre
  PUT    /api/offers/<id>/               → Modifier une offre (entreprise propriétaire)
  DELETE /api/offers/<id>/               → Supprimer une offre (entreprise propriétaire)

  POST   /api/offers/<id>/apply/         → Postuler à une offre (étudiant)
  GET    /api/offers/my-offers/          → Mes offres (entreprise)
  GET    /api/offers/my-applications/    → Mes candidatures (étudiant)
  PATCH  /api/offers/applications/<id>/status/  → Changer statut (entreprise)
"""

from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import InternshipOffer, Application
from .serializers import (
    InternshipOfferSerializer,
    ApplicationSerializer,
    ApplicationStatusSerializer,
)
from .scraper import fetch_moroccan_internships
from ai.services import NLPService
from users.views import IsStudent, IsCompany


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSIONS
# ─────────────────────────────────────────────────────────────────────────────

class IsOfferOwner(permissions.BasePermission):
    """L'entreprise ne peut modifier que SES propres offres."""
    def has_object_permission(self, request, view, obj):
        return obj.company.user == request.user


class IsApplicationOfferOwner(permissions.BasePermission):
    """L'entreprise ne peut gérer que les candidatures de SES offres."""
    def has_object_permission(self, request, view, obj):
        return obj.offer.company.user == request.user


# ─────────────────────────────────────────────────────────────────────────────
# 1. LISTE & CRÉATION D'OFFRES — /api/offers/
# ─────────────────────────────────────────────────────────────────────────────

class InternshipOfferListCreateView(generics.ListCreateAPIView):
    """
    GET  → Liste publique (filtrée, recherchable, paginée)
    POST → Créer une offre (entreprise uniquement)
    """
    serializer_class = InternshipOfferSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'location', 'is_paid', 'duration_months']
    search_fields    = ['title', 'description', 'required_skills', 'location']
    ordering_fields  = ['created_at', 'deadline', 'salary']
    ordering         = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsCompany()]

    def get_queryset(self):
        """Visiteurs anonymes & étudiants voient uniquement les offres actives."""
        user = self.request.user
        if user.is_authenticated and user.is_company:
            # L'entreprise voit toutes les offres (même archivées)
            return InternshipOffer.objects.select_related('company__user').all()
        return InternshipOffer.objects.select_related('company__user').filter(
            status=InternshipOffer.Status.ACTIVE
        )

    def perform_create(self, serializer):
        """Associe automatiquement l'offre au profil entreprise de l'utilisateur."""
        company_profile = self.request.user.company_profile
        serializer.save(company=company_profile)


# ─────────────────────────────────────────────────────────────────────────────
# 2. DÉTAIL / MODIFICATION / SUPPRESSION — /api/offers/<id>/
# ─────────────────────────────────────────────────────────────────────────────

class InternshipOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    → Détail d'une offre (public)
    PUT    → Modifier (entreprise propriétaire)
    PATCH  → Modifier partiellement
    DELETE → Supprimer (entreprise propriétaire)
    """
    serializer_class = InternshipOfferSerializer
    queryset = InternshipOffer.objects.select_related('company__user').all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsCompany(), IsOfferOwner()]


# ─────────────────────────────────────────────────────────────────────────────
# 3. MES OFFRES — /api/offers/my-offers/
# ─────────────────────────────────────────────────────────────────────────────

class MyOffersView(generics.ListAPIView):
    """Liste des offres publiées par l'entreprise connectée."""
    serializer_class = InternshipOfferSerializer
    permission_classes = [IsCompany]

    def get_queryset(self):
        return InternshipOffer.objects.filter(
            company=self.request.user.company_profile
        ).order_by('-created_at')


# ─────────────────────────────────────────────────────────────────────────────
# 4. POSTULER — POST /api/offers/<id>/apply/
# ─────────────────────────────────────────────────────────────────────────────

class ApplyToOfferView(APIView):
    """
    POST → Postuler à une offre (étudiant uniquement).
    Crée une Application avec status=pending.
    """
    permission_classes = [IsStudent]

    def post(self, request, pk):
        try:
            offer = InternshipOffer.objects.get(pk=pk)
        except InternshipOffer.DoesNotExist:
            return Response(
                {"detail": "Offre introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            'offer': offer.pk,
            'cover_letter': request.data.get('cover_letter', ''),
        }
        serializer = ApplicationSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        application = serializer.save(student=request.user.student_profile)

        return Response(
            ApplicationSerializer(application, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. MES CANDIDATURES — /api/offers/my-applications/
# ─────────────────────────────────────────────────────────────────────────────

class MyApplicationsView(generics.ListAPIView):
    """Liste des candidatures de l'étudiant connecté."""
    serializer_class = ApplicationSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user.student_profile
        ).select_related('offer__company').order_by('-applied_at')


class WithdrawApplicationView(APIView):
    """Permet à un étudiant de retirer sa propre candidature en attente."""
    permission_classes = [IsStudent]

    def patch(self, request, pk):
        try:
            application = Application.objects.get(
                pk=pk,
                student=request.user.student_profile,
            )
        except Application.DoesNotExist:
            return Response(
                {"detail": "Candidature introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if application.status != Application.Status.PENDING:
            return Response(
                {"detail": "Seules les candidatures en attente peuvent être retirées."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = Application.Status.WITHDRAWN
        application.save(update_fields=['status'])

        return Response(
            ApplicationSerializer(application, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 6. CANDIDATURES REÇUES — /api/offers/received-applications/
# ─────────────────────────────────────────────────────────────────────────────

class ReceivedApplicationsView(generics.ListAPIView):
    """Liste de toutes les candidatures reçues par l'entreprise connectée."""
    serializer_class = ApplicationSerializer
    permission_classes = [IsCompany]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        return Application.objects.filter(
            offer__company=self.request.user.company_profile
        ).select_related('student__user', 'offer').order_by('-applied_at')


# ─────────────────────────────────────────────────────────────────────────────
# 7. CHANGER STATUT CANDIDATURE — PATCH /api/offers/applications/<id>/status/
# ─────────────────────────────────────────────────────────────────────────────

class ApplicationStatusView(generics.UpdateAPIView):
    """
    PATCH → Changer le statut d'une candidature (accepted / rejected).
    Accessible uniquement par l'entreprise propriétaire de l'offre.
    """
    serializer_class   = ApplicationStatusSerializer
    permission_classes = [IsCompany, IsApplicationOfferOwner]
    http_method_names  = ['patch']

    def get_queryset(self):
        return Application.objects.filter(
            offer__company=self.request.user.company_profile
        )


class MoroccanOfferScrapeView(APIView):
    """Declenche le scraping d'offres de stage oriente Maroc."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        try:
            scrape_stats = fetch_moroccan_internships()
            refresh_payload = None

            if request.data.get("refresh_recommendations", True):
                refresh_payload = NLPService().refresh_all_students()

            return Response(
                {
                    "message": "Scraping Maroc termine avec succes.",
                    "scrape": scrape_stats,
                    "recommendations_refresh": refresh_payload,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Erreur scraping Maroc: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
