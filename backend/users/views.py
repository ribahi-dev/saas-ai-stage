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

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView

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
        return Response(
            {
                "message": "Compte créé avec succès.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )


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
        # Ajout d'un flag indiquant si le profil est complété
        if request.user.is_student:
            data['profile_type'] = 'student'
            data['has_profile'] = hasattr(request.user, 'student_profile')
        elif request.user.is_company:
            data['profile_type'] = 'company'
            data['has_profile'] = hasattr(request.user, 'company_profile')
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
        try:
            return self.request.user.student_profile
        except StudentProfile.DoesNotExist:
            return None

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
        try:
            return self.request.user.company_profile
        except CompanyProfile.DoesNotExist:
            return None

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
        profile = getattr(request.user, 'student_profile', None)
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

        # Validation du type de fichier
        if not (cv_file.name.endswith('.pdf') or cv_file.name.endswith('.docx') or cv_file.name.endswith('.doc')):
            return Response(
                {"detail": "Seuls les fichiers PDF et DOC/DOCX sont acceptés."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sauvegarder le fichier
        profile.cv_file = cv_file
        profile.save()

        # Déclencher l'analyse NLP si disponible
        if NLP_AVAILABLE:
            try:
                nlp = NLPService()
                nlp.process_student_cv(profile)
            except Exception as e:
                # L'upload est réussi même si le NLP échoue
                return Response({
                    "message": "CV uploadé, mais l'analyse NLP a échoué.",
                    "error": str(e),
                    "cv_url": request.build_absolute_uri(profile.cv_file.url),
                }, status=status.HTTP_200_OK)

        return Response({
            "message": "CV uploadé avec succès.",
            "cv_url": request.build_absolute_uri(profile.cv_file.url),
            "nlp_processed": NLP_AVAILABLE,
        }, status=status.HTTP_200_OK)
