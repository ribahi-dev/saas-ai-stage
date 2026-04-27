"""
URL Configuration — Point d'entrée de toutes les routes de l'API.

Architecture des URLs :
  /api/users/    → App users  (auth, profils, upload CV)
  /api/offers/   → App offers (offres de stage, candidatures)
  /api/ai/       → App ai     (recommandations TF-IDF)
  /admin/        → Interface d'administration Django
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Interface admin Django
    path('admin/', admin.site.urls),

    # ── API REST ──────────────────────────────────────────────
    path('api/users/',  include('users.urls')),
    path('api/offers/', include('offers.urls')),
    path('api/ai/',     include('ai.urls')),
]

# En mode DEBUG, servir les fichiers médias (CVs et logos)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
