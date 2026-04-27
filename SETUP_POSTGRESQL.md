# Guide de Configuration PostgreSQL
## Plateforme Intelligente de Recommandation de Stages

---

## Etape 1 — Installer PostgreSQL

Telecharger depuis : https://www.postgresql.org/download/windows/
- Version recommandee : PostgreSQL 16
- Pendant l'installation, choisir un mot de passe pour l'utilisateur `postgres`
- Port par defaut : 5432 (ne pas changer)

---

## Etape 2 — Creer la base de donnees

Ouvrir **pgAdmin** (installe avec PostgreSQL) OU utiliser **psql** en invite de commandes :

### Option A — Via pgAdmin (interface graphique)
1. Ouvrir pgAdmin
2. Clic droit sur "Databases" -> "Create" -> "Database"
3. Nom : `plateforme_stages_db`
4. Owner : `postgres`
5. Cliquer "Save"

### Option B — Via psql (ligne de commande)
```
psql -U postgres
CREATE DATABASE plateforme_stages_db;
\q
```

---

## Etape 3 — Configurer le fichier .env

Editer le fichier `.env` a la racine du projet :

```
SECRET_KEY=django-insecure-change-this-in-production-use-a-real-secret-key
DEBUG=True

DB_NAME=plateforme_stages_db
DB_USER=postgres
DB_PASSWORD=VOTRE_MOT_DE_PASSE_POSTGRESQL
DB_HOST=localhost
DB_PORT=5432
```

**IMPORTANT** : Remplacer `VOTRE_MOT_DE_PASSE_POSTGRESQL` par le mot de passe
choisi lors de l'installation de PostgreSQL.

---

## Etape 4 — Appliquer les migrations

Dans le dossier du projet, avec le venv active :

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate

# Se placer dans le dossier backend
cd backend

# Appliquer les migrations (cree toutes les tables)
..\venv\Scripts\python manage.py migrate

# Creer un superutilisateur administrateur
..\venv\Scripts\python manage.py createsuperuser

# Lancer le serveur
..\venv\Scripts\python manage.py runserver
```

---

## Etape 5 — Verifier que tout fonctionne

Une fois le serveur lance, tester ces URLs dans le navigateur ou Postman :

| Methode | URL                              | Description              |
|---------|----------------------------------|--------------------------|
| GET     | http://localhost:8000/admin/     | Interface admin Django   |
| POST    | http://localhost:8000/api/users/register/ | Creer un compte |
| POST    | http://localhost:8000/api/users/login/    | Obtenir token JWT |
| GET     | http://localhost:8000/api/offers/         | Liste des offres   |

---

## Architecture du Backend (resumee)

```
backend/
+-- core/           # Configuration Django (settings, urls)
+-- users/          # Authentification + Profils
|   +-- models.py   # User, StudentProfile, CompanyProfile
|   +-- views.py    # Register, Login, Me, CV Upload
|   +-- urls.py     # /api/users/...
+-- offers/         # Offres de stage + Candidatures
|   +-- models.py   # InternshipOffer, Application
|   +-- views.py    # CRUD offres, postuler, tableau de bord
|   +-- urls.py     # /api/offers/...
+-- ai/             # Moteur NLP TF-IDF
    +-- models.py   # Recommendation (cache scores)
    +-- services.py # NLPService (pdfplumber + scikit-learn)
    +-- views.py    # GET recommandations, POST refresh
    +-- urls.py     # /api/ai/...
```

---

## API Endpoints complets

### Users (/api/users/)
- POST   /register/        -> Inscription
- POST   /login/           -> Token JWT
- POST   /token/refresh/   -> Rafraichir token
- GET    /me/              -> Mon compte
- PATCH  /me/              -> Modifier compte
- GET    /me/student/      -> Profil etudiant
- PATCH  /me/student/      -> Modifier profil etudiant
- GET    /me/company/      -> Profil entreprise
- PATCH  /me/company/      -> Modifier profil entreprise
- POST   /me/cv/           -> Upload CV (PDF)

### Offers (/api/offers/)
- GET    /                 -> Liste publique (filtres: status, location, is_paid)
- POST   /                 -> Creer une offre (entreprise)
- GET    /<id>/            -> Detail d'une offre
- PUT    /<id>/            -> Modifier offre (entreprise proprietaire)
- DELETE /<id>/            -> Supprimer offre
- POST   /<id>/apply/      -> Postuler (etudiant)
- GET    /my-offers/       -> Mes offres (entreprise)
- GET    /my-applications/ -> Mes candidatures (etudiant)
- GET    /received-applications/ -> Candidatures recues (entreprise)
- PATCH  /applications/<id>/status/ -> Accepter/Refuser candidature

### AI (/api/ai/)
- GET    /recommendations/         -> Mes offres recommandees (etudiant)
- POST   /recommendations/refresh/ -> Recalculer les scores TF-IDF
- GET    /stats/                   -> Stats moteur IA (admin)
