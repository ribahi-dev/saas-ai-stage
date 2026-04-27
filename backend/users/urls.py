"""
users/urls.py — Routes de l'app users

  POST   /api/users/register/        → Créer un compte
  POST   /api/users/login/           → Obtenir tokens JWT
  POST   /api/users/token/refresh/   → Rafraîchir l'access token
  GET    /api/users/me/              → Infos du compte connecté
  PATCH  /api/users/me/              → Modifier compte
  GET    /api/users/me/student/      → Profil étudiant
  PATCH  /api/users/me/student/      → Modifier profil étudiant
  GET    /api/users/me/company/      → Profil entreprise
  PATCH  /api/users/me/company/      → Modifier profil entreprise
  POST   /api/users/me/cv/           → Upload CV (étudiant)
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    MeView,
    StudentProfileView,
    CompanyProfileView,
    CVUploadView,
)

urlpatterns = [
    # ── Authentification ──────────────────────────────────────
    path('register/',       RegisterView.as_view(),      name='user-register'),
    path('login/',          TokenObtainPairView.as_view(), name='user-login'),
    path('token/refresh/',  TokenRefreshView.as_view(),  name='token-refresh'),

    # ── Compte connecté ───────────────────────────────────────
    path('me/',             MeView.as_view(),             name='user-me'),
    path('me/student/',     StudentProfileView.as_view(), name='student-profile'),
    path('me/company/',     CompanyProfileView.as_view(), name='company-profile'),
    path('me/cv/',          CVUploadView.as_view(),       name='cv-upload'),
]
