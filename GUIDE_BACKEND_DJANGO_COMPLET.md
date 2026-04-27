# Guide Backend Django Complet

## 1. Pourquoi ce document existe

Ce document a un objectif tres clair :

- t'expliquer le backend de **ce projet**
- t'expliquer le backend **en general**
- t'expliquer **Django** de zero
- te donner une progression logique pour devenir autonome

Ce n'est pas juste une note technique.
Je l'ecris comme une vraie documentation de comprehension et de formation.

Si tu suis ce guide serieusement, tu pourras :

- comprendre ce backend ligne par ligne
- comprendre pourquoi chaque fichier existe
- comprendre comment construire un backend similaire
- maitriser les bases serieuses de Django
- monter progressivement vers un niveau solide


## 2. Qu'est-ce qu'un backend

Avant Django, il faut comprendre ce qu'est un backend.

Un backend est la partie invisible d'une application.

Le frontend affiche :

- pages
- boutons
- formulaires
- tableaux

Le backend gere :

- les donnees
- la logique metier
- les regles
- la securite
- l'authentification
- la communication avec la base de donnees
- les reponses API

### Exemple concret

Quand un etudiant clique sur "Postuler" :

1. le frontend envoie une requete
2. le backend recoit cette requete
3. le backend verifie si l'utilisateur est connecte
4. il verifie si l'offre existe
5. il verifie si l'etudiant a deja postule
6. il cree la candidature
7. il repond avec du JSON
8. le frontend affiche le resultat

Donc :

- le frontend montre
- le backend decide


## 3. Qu'est-ce qu'une API

Ce backend fonctionne principalement comme une **API REST**.

API veut dire :

**Application Programming Interface**

En pratique, ici, cela veut dire :

- le frontend React parle au backend Django
- ils communiquent avec HTTP
- ils s'echangent du JSON

### Exemples de routes API

- `GET /api/offers/` -> liste des offres
- `POST /api/users/register/` -> creation d'un compte
- `POST /api/offers/12/apply/` -> postuler a une offre
- `GET /api/ai/recommendations/` -> recevoir ses recommandations

### Les methodes HTTP importantes

- `GET` : lire
- `POST` : creer ou lancer une action
- `PATCH` : modifier partiellement
- `PUT` : remplacer
- `DELETE` : supprimer


## 4. Pourquoi Django

Django est un framework Python pour construire des applications web.

Un framework est une structure deja prete qui fournit :

- un systeme de routes
- un systeme de models
- une connexion propre a la base de donnees
- un systeme d'admin
- une architecture de projet
- une authentification
- des outils de securite

### Pourquoi Django est bon pour apprendre

Django est excellent pour apprendre le backend parce qu'il impose une structure claire.

Il t'oblige a separer :

- les donnees
- la logique
- les routes
- la serialisation

Donc si tu comprends Django, tu comprends deja beaucoup de notions fondamentales du backend.


## 5. Les notions Python minimales a connaitre avant Django

Tu n'as pas besoin d'etre un expert Python pour comprendre ce projet.

Tu dois surtout maitriser :

- variables
- fonctions
- listes
- dictionnaires
- `if`
- `for`
- classes
- objets
- imports
- `try/except`

### 5.1 Fonction

Une fonction est un bloc reutilisable.

```python
def calculer_score(a, b):
    return a + b
```

Dans le backend, les fonctions servent a :

- valider
- calculer
- parser
- formater
- reutiliser de la logique

### 5.2 Liste

```python
skills = ["python", "django", "react"]
```

Une liste sert a stocker plusieurs elements.

Dans ce projet :

- competences extraites
- recommandations
- projets
- offres scrapees

### 5.3 Dictionnaire

```python
user = {
    "name": "Ali",
    "city": "Rabat"
}
```

Le dictionnaire est central en backend.
Pourquoi ?
Parce que :

- JSON ressemble a un dictionnaire Python
- beaucoup de donnees de l'API passent par cette structure

### 5.4 Classe

Une classe sert a definir une structure.

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Dans Django, les models sont des classes.


## 6. Vue globale du backend de ce projet

Le backend se trouve dans :

[backend](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend>)

Il contient 4 parties principales :

- `core`
- `users`
- `offers`
- `ai`

### 6.1 `core`

C'est le coeur de configuration.

Il contient :

- `settings.py`
- `urls.py`
- `wsgi.py`
- `asgi.py`

### 6.2 `users`

Cette app gere :

- les comptes
- les roles
- les profils
- l'upload du CV

### 6.3 `offers`

Cette app gere :

- les offres
- les candidatures
- le scraping

### 6.4 `ai`

Cette app gere :

- les recommandations
- l'analyse de CV
- les tendances
- la lettre de motivation
- l'entretien IA


## 7. Comment un projet Django est organise

Un projet Django contient :

- un projet principal
- une ou plusieurs apps

### Projet principal

Dans ce cas :

[backend/core](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/core>)

Il sert a :

- centraliser la config
- declarer les urls globales

### Apps

Une app Django est un bloc fonctionnel autonome.

Ici :

- `users`
- `offers`
- `ai`

Une app contient souvent :

- `models.py`
- `views.py`
- `serializers.py`
- `urls.py`
- `admin.py`
- `migrations/`


## 8. `settings.py` : le cerveau de configuration

Fichier :

[backend/core/settings.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/core/settings.py>)

Ce fichier configure tout le backend.

### Ce qu'on y trouve

- variables d'environnement
- secret key
- debug
- applications installees
- middleware
- base de donnees
- auth user model
- configuration DRF
- JWT
- CORS
- timezone
- media/static

### 8.1 Variables d'environnement

Le backend charge `.env`.

Pourquoi ?

Pour ne pas mettre les secrets directement dans le code.

Exemples :

- `SECRET_KEY`
- `DEBUG`
- plus tard : cles API, identifiants DB

### 8.2 `INSTALLED_APPS`

Cette liste dit a Django quelles apps existent.

Dans ce projet :

- apps natives Django
- `rest_framework`
- `rest_framework_simplejwt`
- `corsheaders`
- `django_filters`
- `users`
- `offers`
- `ai`

### 8.3 `MIDDLEWARE`

Le middleware est une couche qui passe entre la requete et la vue.

Il peut :

- gerer la securite
- gerer les sessions
- gerer l'auth
- gerer les headers CORS

### 8.4 Base de donnees

Actuellement le projet utilise SQLite en local.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Meme si le fichier `requirements.txt` prepare PostgreSQL, le projet tourne actuellement en SQLite.

### 8.5 `AUTH_USER_MODEL`

Le projet utilise un utilisateur personnalise :

```python
AUTH_USER_MODEL = 'users.User'
```

Pourquoi c'est important ?

Parce que cela permet d'ajouter le champ `role` (`student`, `company`, `admin`).

### 8.6 DRF

Le projet utilise Django REST Framework.

`REST_FRAMEWORK` definit :

- auth JWT par defaut
- permission auth par defaut
- rendu JSON
- pagination
- filtres

### 8.7 JWT

`SIMPLE_JWT` configure :

- duree de vie du token access
- duree du refresh token
- rotation

### 8.8 CORS

Comme le frontend est sur un autre port, Django doit autoriser React.

Sinon le navigateur bloque la communication.


## 9. `urls.py` : la carte des routes

Fichier :

[backend/core/urls.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/core/urls.py>)

Ce fichier connecte les grandes familles de routes :

- `/api/users/`
- `/api/offers/`
- `/api/ai/`
- `/admin/`

### Pourquoi c'est important

Si tu veux comprendre un backend, lis toujours les URLs.

Les URLs te disent :

- ce que l'app expose
- comment les fonctionnalites sont decoupees
- ou chercher ensuite


## 10. Les models : le coeur des donnees

Les models sont les classes qui representent les tables SQL.

Chaque ligne en base devient un objet Python.

Dans ce projet, les models les plus importants sont :

- `User`
- `StudentProfile`
- `CompanyProfile`
- `InternshipOffer`
- `Application`
- `Recommendation`


## 11. App `users` en detail

### Fichier principal

[backend/users/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/models.py>)

### 11.1 `User`

Le projet n'utilise pas le model Django standard directement.
Il l'etend avec `AbstractUser`.

Pourquoi ?

Parce qu'on veut un champ `role`.

Le `User` contient :

- username
- email
- password
- first_name
- last_name
- role

### 11.2 Le champ `role`

Ce champ permet de savoir si l'utilisateur est :

- etudiant
- entreprise
- admin

Donc le backend peut adapter :

- permissions
- vues
- donnees renvoyees

### 11.3 `StudentProfile`

Le profil etudiant stocke :

- bio
- telephone
- linkedin
- universite
- filiere
- annee de diplome
- CV
- texte extrait du CV
- competences extraites
- niveau
- projets
- preferences

#### Les nouveaux champs importants

Le projet a evolue vers un vrai matching produit, donc on a ajoute :

- `target_job_titles`
- `preferred_locations`
- `preferred_offer_types`
- `remote_ok`
- `expected_salary`

Ces champs sont importants parce qu'ils permettent d'ameliorer les recommandations.

### 11.4 `CompanyProfile`

Le profil entreprise stocke :

- nom entreprise
- description
- website
- secteur
- ville
- pays
- logo


## 12. Relations entre les models `users`

### `User` -> `StudentProfile`

Relation :

- `OneToOneField`

Cela veut dire :

- un utilisateur etudiant a un seul profil etudiant
- un profil etudiant appartient a un seul utilisateur

### `User` -> `CompanyProfile`

Meme logique :

- un utilisateur entreprise
- un seul profil entreprise

### Pourquoi `OneToOneField`

Parce qu'un compte a un seul profil metier.


## 13. App `users` : serializers

Fichier :

[backend/users/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/serializers.py>)

### A quoi sert un serializer

Il transforme :

- objet Django -> JSON
- JSON -> donnees validees

### 13.1 `UserSerializer`

Utilise pour exposer les infos de base du compte.

### 13.2 `RegisterSerializer`

Il gere l'inscription.

Il fait plusieurs choses :

- valide les mots de passe
- verifie l'unicite de l'email
- cree l'utilisateur
- cree automatiquement le bon profil

### 13.3 `StudentProfileSerializer`

Il expose le profil etudiant.

Maintenant il inclut :

- les infos perso
- les infos academiques
- les champs IA
- les preferences

### 13.4 Validation

Le serializer valide par exemple les types d'offres preferes.

Pourquoi c'est important ?

Parce que le backend ne doit pas faire confiance aux donnees envoyees par le frontend.


## 14. App `users` : views

Fichier :

[backend/users/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/views.py>)

### 14.1 Permissions custom

Tu as :

- `IsStudent`
- `IsCompany`

Ces classes verifient le role.

Elles servent a proteger certaines routes.

### 14.2 `RegisterView`

Route :

- `POST /api/users/register/`

Elle cree un compte.

### 14.3 `MeView`

Route :

- `GET /api/users/me/`
- `PATCH /api/users/me/`

Elle sert a lire ou mettre a jour les infos de base du compte.

### 14.4 `StudentProfileView`

Route :

- `GET/PATCH /api/users/me/student/`

Elle lit ou met a jour le profil etudiant.

### 14.5 `CompanyProfileView`

Route :

- `GET/PATCH /api/users/me/company/`

Elle fait la meme chose pour l'entreprise.

### 14.6 `CVUploadView`

Route :

- `POST /api/users/me/cv/`

Cette vue est tres importante.

Elle :

1. recoit le fichier
2. verifie le type
3. sauvegarde le CV
4. lance l'analyse NLP

Donc ici on a deja un vrai point de contact entre :

- l'upload
- la base
- l'IA


## 15. App `offers` en detail

Fichier model principal :

[backend/offers/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/models.py>)

### 15.1 `InternshipOffer`

Ce model represente une offre.

Champs importants :

- entreprise
- titre
- type d'offre
- description
- competences requises
- localisation
- duree
- remuneration
- statut
- source externe

### Pourquoi `required_skills` est tres important

Parce que ce champ est au coeur du moteur de recommandation.

Le moteur compare :

- competences du CV
- competences et texte de l'offre

### 15.2 `Application`

Ce model represente une candidature.

Il relie :

- un etudiant
- une offre

Et stocke :

- lettre de motivation
- statut
- dates

### Contrainte importante

Il existe une contrainte d'unicite :

- un etudiant ne peut postuler qu'une seule fois a la meme offre


## 16. App `offers` : serializers

Fichier :

[backend/offers/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/serializers.py>)

### 16.1 `InternshipOfferSerializer`

Il expose une offre en JSON.

Il inclut aussi :

- `company_info`
- `applications_count`
- validation de deadline
- validation du salaire si l'offre est payee

### 16.2 `ApplicationSerializer`

Il expose une candidature.

Il inclut :

- infos etudiant
- infos offre

Il contient aussi de la validation :

- deja postule ?
- offre active ?

### 16.3 `ApplicationStatusSerializer`

Utilise pour accepter ou refuser une candidature.


## 17. App `offers` : views

Fichier :

[backend/offers/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/views.py>)

### 17.1 `InternshipOfferListCreateView`

Route :

- `GET /api/offers/`
- `POST /api/offers/`

Elle :

- liste les offres
- cree une offre si l'utilisateur est une entreprise

### 17.2 `InternshipOfferDetailView`

Route :

- `GET /api/offers/<id>/`
- `PUT/PATCH/DELETE /api/offers/<id>/`

Elle gere :

- detail
- edition
- suppression

### 17.3 `MyOffersView`

Permet a une entreprise de voir ses propres offres.

### 17.4 `ApplyToOfferView`

Permet a un etudiant de postuler.

### 17.5 `MyApplicationsView`

Permet a un etudiant de voir ses candidatures.

### 17.6 `WithdrawApplicationView`

Permet a un etudiant de retirer sa candidature si elle est encore en attente.

### 17.7 `ReceivedApplicationsView`

Permet a l'entreprise de voir les candidatures recues.

### 17.8 `ApplicationStatusView`

Permet de changer le statut :

- accepted
- rejected

### 17.9 `MoroccanOfferScrapeView`

Route admin qui declenche le scraping des offres marocaines.


## 18. App `offers` : scraper

Fichier :

[backend/offers/scraper.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/scraper.py>)

Ce fichier est tres important pour comprendre une autre facette du backend :

- integrer des donnees externes

### Les etapes du scraper

1. envoyer une requete HTTP
2. recuperer du HTML
3. parser avec BeautifulSoup
4. detecter les cartes d'offres
5. extraire les champs utiles
6. garder les offres Maroc
7. enrichir les skills
8. creer ou mettre a jour les offres

### Fonctions importantes

- `_fetch_html`
- `_parse_rekrute`
- `_parse_emploi_ma`
- `_build_remote_morocco_offers`
- `_upsert_scraped_offers`
- `fetch_moroccan_internships`

### Pourquoi `update_or_create`

Parce qu'on ne veut pas dupliquer la meme offre a chaque scraping.

On veut :

- creer si elle n'existe pas
- mettre a jour si elle existe


## 19. App `ai` en detail

### Model

[backend/ai/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/models.py>)

Le model `Recommendation` stocke :

- l'etudiant
- l'offre
- le score
- les insights
- la date de calcul

### Pourquoi stocker les recommandations

Pour ne pas recalculer tout a chaque requete.

On utilise donc un cache metier.


## 20. App `ai` : le service NLP

Fichier le plus important :

[backend/ai/services.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/services.py>)

Si tu veux comprendre la partie IA backend, c'est le fichier central.

### Que fait ce service

Il sait :

- lire un CV PDF/DOCX
- nettoyer du texte
- normaliser les competences
- extraire des skills
- estimer un niveau
- calculer une similarite
- calculer un overlap de skills
- appliquer des bonus
- construire des insights
- recalculer les recommandations

### 20.1 `normalize_text`

Nettoie le texte.

Pourquoi c'est important ?

Parce qu'un texte brut contient :

- majuscules
- ponctuation
- formats differents

Et cela rend l'analyse plus difficile.

### 20.2 `canonicalize_skill`

Permet d'unifier les variantes.

Exemple :

- `js` -> `javascript`
- `nodejs` -> `node.js`

### 20.3 `extract_text_from_cv`

Lit le fichier du CV.

Deux cas :

- PDF avec `pdfplumber`
- DOCX avec `python-docx`

### 20.4 `extract_skills_from_text`

Cherche des competences dans le texte.

Il combine :

- patterns predefinis
- tokens techniques detectes

### 20.5 `extract_profile_with_ai`

Essaie d'utiliser Gemini si une cle API existe.

Sinon il repasse en heuristique locale.

Donc le systeme reste utile meme sans IA externe.

### 20.6 `estimate_experience_level`

Essaie d'inferer :

- Stage
- Junior
- Intermediaire
- Confirme

### 20.7 `compute_similarity`

Calcule la similarite semantique avec TF-IDF + cosine similarity.

### 20.8 `compute_skill_overlap`

Calcule a quel point les competences correspondent.

### 20.9 `compute_context_bonus`

Bonus si :

- l'offre est un stage
- l'offre est au Maroc
- l'etudiant est junior
- l'offre est payee

### 20.10 `compute_preference_bonus`

Bonus si l'offre respecte les preferences utilisateur :

- ville preferee
- type prefere
- poste cible
- remote
- salaire

### 20.11 `build_recommendation_insights`

Construit des details exploitables pour l'interface :

- score semantique
- score skills
- bonus
- match skills
- missing skills
- bande de score
- resume

### 20.12 `build_career_insights`

Construit une vue plus produit du profil :

- completion du profil
- forces
- competences prioritaires
- villes cibles
- track recommande
- plan d'action

### 20.13 `process_student_cv`

C'est une des fonctions les plus importantes du backend.

Elle fait tout le pipeline :

1. verifier le CV
2. extraire le texte
3. extraire le profil
4. enrichir le profil etudiant
5. recuperer les offres actives
6. calculer les scores
7. construire les insights
8. stocker les recommandations

### 20.14 `refresh_all_students`

Recalcule toutes les recommandations de tous les etudiants qui ont un CV.


## 21. App `ai` : serializers

Fichier :

[backend/ai/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/serializers.py>)

Le serializer de recommandation expose :

- l'offre detaillee
- le score
- score en pourcentage
- matching skills
- missing skills
- summary
- insights

Donc ici le serializer ne fait pas seulement "passer la donnee".
Il enrichit vraiment la reponse.


## 22. App `ai` : views

Fichier :

[backend/ai/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/views.py>)

### 22.1 `RecommendationListView`

Route :

- `GET /api/ai/recommendations/`

Elle renvoie :

- si le CV existe
- le profil extrait
- les recommendations
- les career insights

### 22.2 `RefreshRecommendationsView`

Route :

- `POST /api/ai/recommendations/refresh/`

Elle relance le calcul.

### 22.3 `AIStatsView`

Route admin :

- `GET /api/ai/stats/`

Elle donne des stats globales.

### 22.4 `GenerateCoverLetterView`

Route :

- `POST /api/ai/cover-letter/<offer_id>/`

Elle utilise Gemini pour generer une lettre.

### 22.5 `InterviewBotView`

Route :

- `POST /api/ai/interview/<offer_id>/`

Elle simule un entretien.

### 22.6 `MarketTrendsView`

Route :

- `GET /api/ai/market-trends/`

Elle analyse les offres en base pour produire :

- top skills
- top cities
- top platforms


## 23. Les migrations

Dossier :

- `backend/users/migrations/`
- `backend/offers/migrations/`
- `backend/ai/migrations/`

Les migrations sont l'historique des changements de structure SQL.

Quand tu modifies un model :

1. tu lances `makemigrations`
2. Django cree une migration
3. tu lances `migrate`
4. la base de donnees est mise a jour

### Pourquoi c'est essentiel

Parce que modifier un model Python ne modifie pas automatiquement la base.


## 24. Le cycle complet d'une fonctionnalite backend

Pour bien comprendre Django, il faut comprendre le cycle complet.

Prenons l'exemple : **un etudiant met a jour ses preferences**

### Etape 1

Le frontend envoie :

- `PATCH /api/users/me/student/`

### Etape 2

La route `users/urls.py` envoie vers la vue.

### Etape 3

La vue `StudentProfileView` recoit la requete.

### Etape 4

Elle verifie la permission :

- est-ce un etudiant ?

### Etape 5

Elle instancie le serializer.

### Etape 6

Le serializer valide les donnees.

### Etape 7

Le serializer sauvegarde en base.

### Etape 8

La vue renvoie le JSON de reponse.

Ce cycle est la base de presque tout le backend.


## 25. Comment ce backend a probablement ete construit

Tu m'as dit que le projet venait beaucoup du vibe coding.
Donc je te donne une lecture d'ingenieur sur l'ordre logique de construction.

### Phase 1 - Base du projet

On cree :

- le projet Django
- les apps
- les settings
- l'utilisateur custom

### Phase 2 - Auth et profils

On cree :

- register
- login JWT
- profils etudiant / entreprise

### Phase 3 - Offres et candidatures

On cree :

- model offre
- model candidature
- CRUD offres
- postulation

### Phase 4 - Recommandation simple

On ajoute :

- upload CV
- extraction texte
- TF-IDF
- score

### Phase 5 - IA enrichie

On ajoute :

- extraction de skills
- niveau
- projets
- lettre IA
- entretien IA

### Phase 6 - Scraping

On ajoute :

- import d'offres externes
- fallback Maroc

### Phase 7 - Produit plus mature

On ajoute :

- preferences utilisateur
- insights
- career coaching
- dashboards plus utiles


## 26. Ce qu'il faut comprendre pour maitriser Django en general

Si ton but est de maitriser Django, il faut apprendre dans cet ordre.

### Niveau 1

- Python bases
- projet Django
- app Django
- model
- admin
- URLs
- view

### Niveau 2

- forms
- serializers
- permissions
- auth
- relations SQL
- migrations

### Niveau 3

- API REST
- JWT
- filtres
- pagination
- architecture d'apps
- services metier

### Niveau 4

- tests
- caching
- taches async
- optimisation DB
- securite
- deployment


## 27. Les erreurs classiques d'un debutant Django

### Erreur 1

Lire seulement le frontend et oublier les models.

### Erreur 2

Croire que la view contient tout.

Non.
La logique est partagee entre :

- models
- serializers
- views
- services

### Erreur 3

Ne pas comprendre les relations entre tables.

### Erreur 4

Modifier le model sans faire de migration.

### Erreur 5

Confondre :

- authentification
- permission

Authentification = qui es-tu ?
Permission = as-tu le droit ?

### Erreur 6

Voir Django comme une magie noire.

En realite, Django est une architecture tres reguliere.


## 28. Comment lire ce backend comme un ingenieur

Quand tu analyses une fonctionnalite, fais toujours ce trajet :

1. URL
2. View
3. Serializer
4. Model
5. Eventuel service

### Exemple : recommandations

1. `core/urls.py`
2. `ai/urls.py`
3. `ai/views.py`
4. `ai/serializers.py`
5. `ai/models.py`
6. `ai/services.py`
7. `users/models.py`
8. `offers/models.py`

En suivant cet ordre, tu evites de te perdre.


## 29. Ordre de lecture ideal des fichiers backend

Si tu veux vraiment comprendre ce backend, lis dans cet ordre :

1. [backend/core/settings.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/core/settings.py>)
2. [backend/core/urls.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/core/urls.py>)
3. [backend/users/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/models.py>)
4. [backend/offers/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/models.py>)
5. [backend/ai/models.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/models.py>)
6. [backend/users/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/serializers.py>)
7. [backend/offers/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/serializers.py>)
8. [backend/ai/serializers.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/serializers.py>)
9. [backend/users/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/users/views.py>)
10. [backend/offers/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/views.py>)
11. [backend/ai/views.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/views.py>)
12. [backend/ai/services.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/ai/services.py>)
13. [backend/offers/scraper.py](</C:/Users/elmeh/Desktop/plateforme-stages V1/backend/offers/scraper.py>)


## 30. Plan de maitrise backend recommande

Voici un vrai plan pedagogue.

### Etape 1 - Fondations

Apprendre :

- fonctions Python
- listes
- dictionnaires
- classes

### Etape 2 - Django data layer

Apprendre :

- model Django
- field types
- relations
- migrations

### Etape 3 - API layer

Apprendre :

- serializer
- view
- URL
- request / response

### Etape 4 - Auth

Apprendre :

- JWT
- permissions
- current user

### Etape 5 - Services metier

Apprendre :

- sortir la logique complexe des views
- construire un service comme `NLPService`

### Etape 6 - Produit reel

Apprendre :

- filtres
- pagination
- handling erreurs
- validation

### Etape 7 - Niveau avance

Apprendre :

- optimisation
- tests
- async jobs
- deployment


## 31. Ce que tu dois retenir absolument

Si tu oublies tout le reste, retiens ca :

### 1

Le backend sert a gerer les donnees et la logique metier.

### 2

Django organise le backend proprement.

### 3

Les models definissent les donnees.

### 4

Les serializers transforment et valident les donnees.

### 5

Les views executent les actions metier.

### 6

Les urls relient les routes aux vues.

### 7

Les services portent la logique complexe.

### 8

Ce projet est un backend API oriente produit, pas juste une base CRUD.


## 32. Conclusion

Tu voulais le meilleur guide backend possible pour comprendre :

- ce backend
- Django
- la logique backend en general

Ce document est fait pour ca.

Il faut maintenant l'utiliser intelligemment :

- lire une section
- ouvrir les fichiers lies
- faire le lien avec le code reel
- reformuler avec tes propres mots

Le vrai objectif n'est pas de memoriser.
Le vrai objectif est de devenir capable de dire :

> je sais comment une requete entre, comment Django la traite, comment la base est lue, comment la logique metier s'execute, et comment la reponse est renvoyee.

Quand tu sauras faire ca, tu ne seras plus en train de "subir" le backend.
Tu commenceras a le maitriser.
