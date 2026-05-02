"""
Django Settings — Plateforme Intelligente de Recommandation de Stages
======================================================================
Architecture : Headless API (Django + DRF) consommée par React.js

SÉCURITÉ : Toutes les valeurs sensibles sont lues depuis le fichier .env
via python-dotenv. Ne jamais coder de secrets en dur dans ce fichier.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 1. CHEMINS & VARIABLES D'ENVIRONNEMENT
# ---------------------------------------------------------------------------

# Racine du projet : le dossier `backend/`
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger .env avec utf-8-sig pour gerer le BOM (Byte Order Mark) Windows
load_dotenv(BASE_DIR.parent / '.env', encoding='utf-8-sig', override=True)

# --- Correctif Windows : purger les variables systeme PostgreSQL ---
# Sur Windows, certaines variables PGPASSWORD / PGPASSFILE heritees du systeme
# peuvent contenir des caracteres Windows-1252 (0xe9 = e accent aigu) qui
# causent un UnicodeDecodeError dans psycopg2. On les supprime pour forcer
# l'utilisation exclusive de nos valeurs .env.
for _pg_var in ('PGPASSWORD', 'PGPASSFILE', 'PGSERVICE', 'PGSERVICEFILE',
                'PGUSER', 'PGDATABASE', 'PGHOST', 'PGPORT'):
    os.environ.pop(_pg_var, None)


# ─────────────────────────────────────────────────────────────────────────────
# 2. SÉCURITÉ
# ─────────────────────────────────────────────────────────────────────────────

DEBUG = os.getenv('DEBUG', 'True') == 'True'
_secret_key = os.getenv('SECRET_KEY', '').strip()
if not _secret_key and not DEBUG:
    raise ImproperlyConfigured(
        "SECRET_KEY doit etre defini dans .env lorsque DEBUG=False."
    )
SECRET_KEY = _secret_key or 'django-insecure-dev-only-change-for-local'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]


# ─────────────────────────────────────────────────────────────────────────────
# 3. APPLICATIONS INSTALLÉES
# ─────────────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Applications Django natives
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Packages tiers
    'rest_framework',           # Django REST Framework : notre moteur d'API
    'rest_framework_simplejwt', # Authentification par tokens JWT
    'corsheaders',              # Gestion des requêtes Cross-Origin (React → Django)

    # Filtrage côté API
    'django_filters',

    # Nos applications métier
    'users',                    # Gestion des utilisateurs (Étudiant / Entreprise)
    'offers',                   # Offres de stage + Candidatures
    'ai',                       # Moteur de recommandation TF-IDF
]


# ─────────────────────────────────────────────────────────────────────────────
# 4. MIDDLEWARE
# Pourquoi cet ordre ? CorsMiddleware DOIT être le plus haut possible,
# avant CommonMiddleware, pour intercepter les requêtes OPTIONS (preflight).
# ─────────────────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ← DOIT être en premier
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ─────────────────────────────────────────────────────────────────────────────
# 5. URLS & WSGI
# ─────────────────────────────────────────────────────────────────────────────

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'


# ─────────────────────────────────────────────────────────────────────────────
# 6. TEMPLATES (nécessaire pour l'interface admin Django)
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 7. BASE DE DONNÉES — PostgreSQL
# Driver Python : psycopg2-binary (pip install psycopg2-binary)
# Les credentials sont lus depuis .env → jamais en dur dans le code.
# ─────────────────────────────────────────────────────────────────────────────

_db_name = os.getenv('DB_NAME', '').strip()
if _db_name:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _db_name,
            'USER': os.getenv('DB_USER', 'postgres').strip() or 'postgres',
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost').strip() or 'localhost',
            'PORT': os.getenv('DB_PORT', '5432').strip() or '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# 8. MODÈLE UTILISATEUR PERSONNALISÉ
# Pourquoi AUTH_USER_MODEL ? C'est une RÈGLE D'OR Django :
# toujours déclarer un User custom DÈS le début. Impossible de le changer
# après les premières migrations sans tout casser. On le prépare maintenant.
# ─────────────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'users.User'


# ─────────────────────────────────────────────────────────────────────────────
# 9. DJANGO REST FRAMEWORK — Configuration globale de l'API
# ─────────────────────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    # Toute route API nécessite par défaut un token JWT valide
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # Format JSON pour toutes les réponses
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # Pagination globale : 20 résultats par page
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Filtrage et recherche via query params
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.getenv('DRF_THROTTLE_ANON', '120/hour'),
        'user': os.getenv('DRF_THROTTLE_USER', '4000/hour'),
        'gemini_user': os.getenv('DRF_THROTTLE_GEMINI', '90/hour'),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 9-bis. SIMPLE JWT — Durée de vie des tokens
# ─────────────────────────────────────────────────────────────────────────────

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ─────────────────────────────────────────────────────────────────────────────
# 10. CORS — Autoriser React (Vite port 5173) à appeler Django (port 8000)
# ─────────────────────────────────────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # Vite dev server
    'http://127.0.0.1:5173',   # Vite dev server via IP
    'http://localhost:3000',   # Create React App (au cas où)
    'http://127.0.0.1:3000',   # CRA via IP
    'http://localhost:4173',   # Vite preview
    'http://127.0.0.1:4173',   # Vite preview via IP
]

# Autoriser l'envoi de cookies/credentials cross-origin
CORS_ALLOW_CREDENTIALS = True

# Google OAuth (web) — verifier les ID tokens JWT emis par Sign In With Google
# Meme valeur que la "Client ID" JavaScript dans la console Google Cloud
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '').strip()


# ─────────────────────────────────────────────────────────────────────────────
# 11. VALIDATION DES MOTS DE PASSE
# ─────────────────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─────────────────────────────────────────────────────────────────────────────
# 12. INTERNATIONALISATION
# ─────────────────────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True


# ─────────────────────────────────────────────────────────────────────────────
# 13. FICHIERS STATIQUES & MÉDIAS
# Les fichiers médias = CVs uploadés par les étudiants (Phase 4)
# ─────────────────────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ─────────────────────────────────────────────────────────────────────────────
# 14. CLÉ PRIMAIRE PAR DÉFAUT
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
