# SaaS AI Stage

Plateforme SaaS de recommandation intelligente de stages, orientee etudiants, stagiaires et entreprises.

Le projet combine :

- un backend Django REST API
- un frontend React + TypeScript
- un moteur de recommandation IA/NLP
- un scraping d'offres marocaines
- des outils d'aide a la candidature (lettre de motivation, entretien IA, tendances marche)

## Vision

L'objectif du produit est de devenir une application utile et differenciante pour :

- les etudiants qui cherchent un stage plus vite et plus intelligemment
- les jeunes talents qui veulent comprendre leur positionnement sur le marche
- les entreprises qui veulent publier et gerer leurs offres

L'idee centrale n'est pas seulement de lister des offres, mais de proposer un vrai moteur de matching :

- analyse du CV
- extraction des competences
- prise en compte des preferences utilisateur
- scoring explicable
- plan d'action pour progresser

## Fonctionnalites principales

### Etudiant

- inscription / connexion JWT
- profil etudiant
- upload de CV PDF ou DOCX
- extraction automatique du profil
- recommandations IA personnalisees
- filtres par ville et type d'offre
- candidature
- retrait d'une candidature en attente
- generation de lettre de motivation
- simulation d'entretien IA
- career insights :
  - forces detectees
  - competences a renforcer
  - villes pertinentes
  - track recommande
  - plan d'action

### Entreprise

- inscription entreprise
- gestion du profil entreprise
- creation et gestion d'offres
- consultation des candidatures recues
- changement de statut des candidatures

### Admin / plateforme

- admin Django
- scraping d'offres marocaines
- recalcul global des recommandations
- tendances du marche :
  - competences les plus demandees
  - villes les plus actives
  - plateformes les plus utiles

## Stack technique

### Backend

- Python
- Django
- Django REST Framework
- JWT avec `djangorestframework-simplejwt`
- `django-filter`
- `django-cors-headers`
- `pdfplumber`
- `python-docx`
- `scikit-learn`
- `requests`
- `beautifulsoup4`
- `google-generativeai`

### Frontend

- React
- TypeScript
- Vite
- Axios
- React Router
- Tailwind CSS
- Heroicons

## Architecture

### Backend

Le backend est structure en apps Django :

- `users/` : comptes, roles, profils, upload CV
- `offers/` : offres, candidatures, scraping
- `ai/` : recommandations, NLP, tendances, IA auxiliaire
- `core/` : configuration globale du projet

### Frontend

Le frontend est structure en :

- `src/pages/` : pages principales
- `src/components/` : composants reutilisables
- `src/contexts/` : auth globale
- `src/services/` : client API Axios

## Moteur de recommandation

Le moteur IA du projet repose sur un score hybride.

### Sources de signal

- similarite semantique CV / offre avec TF-IDF
- overlap de competences
- bonus contextuel :
  - offre de type stage
  - localisation Maroc
  - offre remuneree
  - niveau junior / stage
- bonus de preferences :
  - postes cibles
  - villes preferees
  - types d'offres preferes
  - remote
  - salaire vise

### Sorties utiles

Chaque recommandation peut inclure :

- score global
- score semantique
- score d'overlap de competences
- bonus de contexte
- bonus de preferences
- competences deja alignees
- competences a renforcer
- resume de recommandation

Le dashboard etudiant agregre aussi des `career insights` pour transformer la reco en coaching produit.

## Scraping Maroc

Le projet inclut un scraper orienté Maroc.

Sources visees :

- Rekrute
- Emploi.ma
- fallback distant
- fallback local si le reseau ne remonte rien

Le scraper :

- recupere le HTML
- parse les cartes d'offres
- detecte les offres pertinentes pour le Maroc
- normalise les donnees
- enrichit les competences
- cree ou met a jour les offres
- peut relancer les recommandations ensuite

## Installation

### Prerequis

- Python 3.11+
- Node.js 18+
- npm

## Setup backend

Depuis la racine du projet :

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Creer un fichier `.env` a la racine avec au minimum :

```env
SECRET_KEY=change-me
DEBUG=True
```

Appliquer les migrations :

```powershell
venv\Scripts\python.exe backend\manage.py migrate
```

Lancer le backend :

```powershell
venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

Backend disponible sur :

- `http://127.0.0.1:8000/`
- admin : `http://127.0.0.1:8000/admin/`

## Setup frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend disponible sur :

- `http://127.0.0.1:5173/`

## Scripts utiles

### Backend

Verifier le projet :

```powershell
venv\Scripts\python.exe backend\manage.py check
```

Scraper les offres marocaines :

```powershell
venv\Scripts\python.exe backend\manage.py scrape_morocco_offers
```

Scraper sans recalculer les recos :

```powershell
venv\Scripts\python.exe backend\manage.py scrape_morocco_offers --skip-refresh
```

### Frontend

```powershell
npm run dev
npm run build
npm run lint
```

## API principale

### Users

- `POST /api/users/register/`
- `POST /api/users/login/`
- `POST /api/users/token/refresh/`
- `GET /api/users/me/`
- `GET/PATCH /api/users/me/student/`
- `GET/PATCH /api/users/me/company/`
- `POST /api/users/me/cv/`

### Offers

- `GET /api/offers/`
- `POST /api/offers/`
- `GET /api/offers/<id>/`
- `POST /api/offers/<id>/apply/`
- `GET /api/offers/my-offers/`
- `GET /api/offers/my-applications/`
- `PATCH /api/offers/applications/<id>/withdraw/`
- `GET /api/offers/received-applications/`
- `PATCH /api/offers/applications/<id>/status/`
- `POST /api/offers/scrape/morocco/`

### AI

- `GET /api/ai/recommendations/`
- `POST /api/ai/recommendations/refresh/`
- `GET /api/ai/stats/`
- `GET /api/ai/market-trends/`
- `POST /api/ai/cover-letter/<offer_id>/`
- `POST /api/ai/interview/<offer_id>/`

## Etat actuel du projet

Le projet est deja plus qu'un simple prototype visuel.

Il dispose de :

- backend API fonctionnel
- frontend utilisable
- matching IA exploitable
- preferences etudiant
- dashboards utiles
- scraping d'offres
- base solide pour une evolution SaaS

Mais il reste encore des etapes pour passer au niveau production complet :

- tests backend/frontend plus solides
- taches asynchrones pour NLP et scraping
- notifications email
- shortlist / favoris
- analytics entreprise
- observabilite et logs produit
- securite prod et CI/CD
- billing / abonnement si monetisation

## Roadmap produit conseillee

### Phase 1 - Qualite produit

- tests unitaires et API
- seed data plus riche
- onboarding plus fort
- gestion erreurs plus polie

### Phase 2 - SaaS etudiant

- favoris / shortlist
- alertes personnalisees
- suivi de progression
- score de profil

### Phase 3 - SaaS entreprise

- tableau de bord candidats
- matching inverse offre -> etudiants
- pipeline de recrutement
- export / reporting

### Phase 4 - Production

- Postgres en prod
- Celery / RQ pour jobs background
- stockage fichiers externe
- monitoring et securite

## Documents utiles

- guide de comprehension du projet :
  [GUIDE_COMPREHENSION_PROJET.md](./GUIDE_COMPREHENSION_PROJET.md)

- setup PostgreSQL :
  [SETUP_POSTGRESQL.md](./SETUP_POSTGRESQL.md)

## Auteur / contexte

Ce projet a ete fortement accelere avec de l'IA, puis retravaille avec une logique d'ingenierie produit pour le rendre plus coherent, plus utile et plus proche d'une vraie application SaaS.
