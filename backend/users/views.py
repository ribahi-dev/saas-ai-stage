"""
users/views.py — Vues API pour l'authentification et les profils

Endpoints implémentés :
  POST /api/users/register/          → Inscription (public)
  POST /api/users/login/             → Login JWT (public)
  POST /api/users/token/refresh/     → Rafraîchir token (public)
  GET  /api/users/me/                → Mon compte (authentifié)
  GET/PATCH /api/users/me/student/   → Mon profil étudiant (authentifié)
  GET/PATCH /api/users/me/company/   → Mon profil entreprise (authentifié)
  POST /api/users/me/cv/             → Upload CV (étudiant uniquement)
"""

import logging
import re
from secrets import token_hex

from django.conf import settings
from django.db import transaction

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from .models import StudentProfile, CompanyProfile
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    StudentProfileSerializer,
    CompanyProfileSerializer,
)

# Import du service NLP (Phase 4 — appelé lors de l'upload du CV)
try:
    from ai.services import NLPService
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

User = get_user_model()

logger = logging.getLogger(__name__)


def _google_username_candidate(email: str, google_sub: str) -> str:
    """Construit un username unique a partir de l email et du sub Google."""
    local = email.split('@')[0]
    slug = re.sub(r'[^\w.-]', '_', local, flags=re.UNICODE)[:70] or 'user'
    tail = google_sub[-12:] if google_sub else token_hex(4)
    base = f'{slug}_g{tail}'
    if len(base) > 150:
        base = f'{base[:130]}_{tail}'
    candidate = base
    n = 0
    while User.objects.filter(username=candidate).exists():
        n += 1
        extra = token_hex(2)
        candidate = f'{base[:125]}_{extra}_{n}'
        candidate = candidate[:150]
    return candidate

MAX_CV_BYTES = 5 * 1024 * 1024


def _validate_cv_file(cv_file) -> str | None:
    """Retourne un message d'erreur ou None si le fichier est acceptable."""
    name = (cv_file.name or "").lower()
    if cv_file.size > MAX_CV_BYTES:
        return "Fichier trop volumineux (maximum 5 Mo)."
    if not (name.endswith(".pdf") or name.endswith(".docx") or name.endswith(".doc")):
        return "Seuls les fichiers PDF et DOC/DOCX sont acceptés."
    head = cv_file.read(8)
    cv_file.seek(0)
    if name.endswith(".pdf") and not head.startswith(b"%PDF"):
        return "Le fichier ne correspond pas à un PDF valide."
    if name.endswith(".docx") and not head.startswith(b"PK\x03\x04"):
        return "Le fichier ne correspond pas à un document DOCX valide."
    if name.endswith(".doc") and not head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "Le fichier ne correspond pas à un document DOC valide."
    return None


def ensure_role_profile(user):
    """
    Garantit que le profil lie au role existe.
    Utile apres OAuth, anciennes donnees ou imports manuels.
    """
    if not user.is_authenticated:
        return None
    if user.is_student:
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        return profile
    if user.is_company:
        profile, _ = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                "company_name": (
                    f"{user.first_name} {user.last_name}".strip()
                    or user.username
                )[:200],
            },
        )
        return profile
    return None


# ─────────────────────────────────────────────────────────────────────────────
# PERMISSIONS PERSONNALISÉES
# ─────────────────────────────────────────────────────────────────────────────

class IsStudent(permissions.BasePermission):
    """Autorise uniquement les utilisateurs avec le rôle 'student'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsCompany(permissions.BasePermission):
    """Autorise uniquement les utilisateurs avec le rôle 'company'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_company


# ─────────────────────────────────────────────────────────────────────────────
# 1. REGISTER — POST /api/users/register/
# ─────────────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """
    Endpoint d'inscription — accessible sans authentification.
    Crée le compte User + le profil associé (StudentProfile ou CompanyProfile).
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Compte créé avec succès.",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────────────────────────────────────────
# 1-bis GOOGLE AUTH — POST /api/users/google/
# ─────────────────────────────────────────────────────────────────────────────


class GoogleAuthView(APIView):
    """
    Connexion ou inscription via Google Sign-In (ID JWT).
    Body JSON : { \"credential\": \"...\", \"role\": \"student\"|\"company\" (nouveau compte) }
    Reponse identique au login classique SimpleJWT : access + refresh.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '') or ''
        if not client_id:
            return Response(
                {'detail': 'Connexion Google non configuree sur le serveur.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        credential = (
            request.data.get('credential')
            or request.data.get('id_token')
            or ''
        ).strip()
        if not credential:
            return Response(
                {'detail': 'Jeton Google manquant (champ credential).'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token as google_id_token

            idinfo = google_id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                client_id,
            )
        except ValueError:
            logger.warning('Verification du jeton Google refusee.')
            return Response(
                {'detail': 'Jeton Google invalide ou expire.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = (idinfo.get('email') or '').strip().lower()
        if not email:
            return Response(
                {'detail': "L'email n'est pas present sur ce compte Google."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if idinfo.get('email_verified') is False:
            return Response(
                {'detail': 'Cette adresse Google nest pas marquee comme verifiee.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sub = str(idinfo.get('sub') or '')
        given = (idinfo.get('given_name') or '')[:150]
        family = (idinfo.get('family_name') or '')[:150]

        requested_role = request.data.get('role') or User.Role.STUDENT
        if requested_role not in (User.Role.STUDENT, User.Role.COMPANY):
            requested_role = User.Role.STUDENT

        try:
            with transaction.atomic():
                user = User.objects.select_for_update().filter(email__iexact=email).first()
                if user is None:
                    username = _google_username_candidate(email, sub)
                    user = User(
                        username=username,
                        email=email,
                        first_name=given,
                        last_name=family,
                        role=requested_role,
                    )
                    user.set_unusable_password()
                    user.save()
                    if requested_role == User.Role.STUDENT:
                        StudentProfile.objects.create(user=user)
                    else:
                        CompanyProfile.objects.create(
                            user=user,
                            company_name=username.replace('_', ' ')[:200],
                        )
                    logger.info('Compte cree via Google: %s', email)
                else:
                    updates = []
                    if not (user.first_name or '').strip() and given:
                        user.first_name = given
                        updates.append('first_name')
                    if not (user.last_name or '').strip() and family:
                        user.last_name = family
                        updates.append('last_name')
                    if updates:
                        user.save(update_fields=updates)
                ensure_role_profile(user)
        except Exception:
            logger.exception('Erreur creation / liaison compte Google (%s)', email)
            return Response(
                {'detail': 'Erreur serveur lors de la liaison du compte Google.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 2. ME — GET /api/users/me/
# ─────────────────────────────────────────────────────────────────────────────

class MeView(APIView):
    """
    Retourne les informations du compte connecté.
    Inclut l'URL du profil associé selon le rôle.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        ensure_role_profile(request.user)
        # Ajout d'un flag indiquant si le profil est complété
        if request.user.is_student:
            data['profile_type'] = 'student'
            data['has_profile'] = True
        elif request.user.is_company:
            data['profile_type'] = 'company'
            data['has_profile'] = True
        return Response(data)

    def patch(self, request):
        """Mise à jour des champs de base du compte (first_name, last_name, email)."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# 3. STUDENT PROFILE — GET/PATCH /api/users/me/student/
# ─────────────────────────────────────────────────────────────────────────────

class StudentProfileView(APIView):
    """Récupère et met à jour le profil étudiant de l'utilisateur connecté."""
    permission_classes = [IsStudent]

    def get_profile(self):
        return ensure_role_profile(self.request.user)

    def get(self, request):
        profile = self.get_profile()
        if not profile:
            return Response(
                {"detail": "Profil étudiant introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(StudentProfileSerializer(profile).data)

    def patch(self, request):
        profile = self.get_profile()
        if not profile:
            return Response(
                {"detail": "Profil étudiant introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# 4. COMPANY PROFILE — GET/PATCH /api/users/me/company/
# ─────────────────────────────────────────────────────────────────────────────

class CompanyProfileView(APIView):
    """Récupère et met à jour le profil entreprise de l'utilisateur connecté."""
    permission_classes = [IsCompany]

    def get_profile(self):
        return ensure_role_profile(self.request.user)

    def get(self, request):
        profile = self.get_profile()
        if not profile:
            return Response(
                {"detail": "Profil entreprise introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(CompanyProfileSerializer(profile).data)

    def patch(self, request):
        profile = self.get_profile()
        if not profile:
            return Response(
                {"detail": "Profil entreprise introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = CompanyProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ─────────────────────────────────────────────────────────────────────────────
# 5. CV UPLOAD — POST /api/users/me/cv/
# ─────────────────────────────────────────────────────────────────────────────

class CVUploadView(APIView):
    """
    Upload du CV en PDF.
    - Sauvegarde le fichier dans media/cvs/
    - Déclenche automatiquement l'extraction NLP (si Phase 4 disponible)
    """
    permission_classes = [IsStudent]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = ensure_role_profile(request.user)
        if not profile:
            return Response(
                {"detail": "Profil étudiant introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )

        if 'cv_file' not in request.FILES:
            return Response(
                {"detail": "Aucun fichier fourni. Utilisez le champ 'cv_file'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cv_file = request.FILES['cv_file']
        validation_error = _validate_cv_file(cv_file)
        if validation_error:
            return Response(
                {"detail": validation_error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sauvegarder le fichier
        profile.cv_file = cv_file
        profile.save()

        # Déclencher l'analyse NLP si disponible
        if NLP_AVAILABLE:
            try:
                nlp = NLPService()
                nlp.process_student_cv(profile)
            except Exception:
                logger.exception("Analyse NLP apres upload CV (user=%s)", request.user.pk)
                return Response(
                    {
                        "message": "CV uploadé, mais l'analyse automatique a échoué.",
                        "cv_url": request.build_absolute_uri(profile.cv_file.url),
                    },
                    status=status.HTTP_200_OK,
                )

        return Response({
            "message": "CV uploadé avec succès.",
            "cv_url": request.build_absolute_uri(profile.cv_file.url),
            "nlp_processed": NLP_AVAILABLE,
        }, status=status.HTTP_200_OK)
