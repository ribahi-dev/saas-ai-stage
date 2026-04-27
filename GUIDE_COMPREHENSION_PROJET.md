# Guide de comprehension du projet

## 1. Pourquoi ce document existe

Ce projet a ete construit en grande partie avec de l'aide IA. Ce n'est pas un probleme en soi, mais cela cree souvent une situation difficile:

- le projet fonctionne
- les fichiers existent
- les technologies sont la
- mais le proprietaire du projet ne comprend pas encore vraiment ce qu'il a entre les mains

Ce document a ete ecrit pour corriger ca.

Le but n'est pas seulement de t'expliquer "ce que fait le projet".
Le but est de t'aider a:

- comprendre la logique complete du projet
- comprendre les technologies utilisees
- savoir dans quel ordre apprendre
- savoir quelles notions sont obligatoires
- passer d'un niveau debutant a un niveau autonome
- construire une vraie base pour devenir fort plus tard


## 2. Resume tres simple du projet

Ce projet est une plateforme web de recommandation de stages.

Il permet a:

- un etudiant de creer un compte, uploader son CV, recevoir des recommandations, consulter des offres et postuler
- une entreprise de creer un compte, publier des offres et gerer les candidatures
- un administrateur de gerer le systeme et lancer le scraping d'offres marocaines

Le projet contient aussi une partie "IA" qui sert a:

- lire le CV
- extraire des competences
- comparer le CV aux offres
- calculer un score de compatibilite
- suggerer les meilleures offres


## 3. Architecture generale

Le projet est coupe en 2 grandes parties:

### Backend

Dossier: `backend/`

Le backend est le cerveau du projet.
Il gere:

- les utilisateurs
- les profils
- les offres
- les candidatures
- le stockage des donnees
- l'authentification
- les recommandations
- le scraping

Technologie principale:

- Python
- Django
- Django REST Framework

### Frontend

Dossier: `frontend/`

Le frontend est la partie visible du projet.
Il gere:

- les pages
- les formulaires
- les boutons
- l'affichage des offres
- l'affichage des recommandations
- les appels vers le backend

Technologie principale:

- React
- TypeScript
- Vite
- Tailwind CSS


## 4. Ce qu'il faut comprendre en premier

Tu n'as pas besoin d'apprendre toute l'informatique pour comprendre ce projet.

Tu dois d'abord comprendre ces 6 blocs:

1. Python: fonctions, listes, dictionnaires, classes
2. Django: models, serializers, views, urls
3. API: HTTP, JSON, JWT
4. React: composants, state, effect, routing
5. IA du projet: TF-IDF, similarite cosinus, extraction de skills
6. Scraping: requete HTTP, HTML, parsing

Si tu comprends vraiment ces 6 blocs, tu comprendras deja tres bien le projet.


## 5. Partie 1 - Python

Python est le langage du backend.

Tu n'as pas besoin de tout savoir.
Pour ce projet, il faut surtout maitriser:

- les variables
- les fonctions
- les listes
- les dictionnaires
- les conditions
- les boucles
- les classes
- les objets
- les imports
- les exceptions simples

### 5.1 Les fonctions

Une fonction est un bloc de code reutilisable.

Exemple mental:

- tu donnes une entree
- la fonction travaille
- elle renvoie un resultat

Exemple:

```python
def addition(a, b):
    return a + b
```

Dans le projet, les fonctions servent partout:

- extraire le texte du CV
- calculer un score
- normaliser un texte
- parser une page HTML
- filtrer des donnees

Ce qu'il faut comprendre:

- une fonction peut recevoir des parametres
- une fonction peut retourner une valeur
- une fonction peut etre appelee par une autre fonction

### 5.2 Les listes

Une liste sert a stocker plusieurs elements.

Exemple:

```python
skills = ["python", "django", "react"]
```

Dans le projet, on utilise des listes pour:

- stocker des competences
- stocker des recommandations
- stocker des offres scrapees
- stocker des projets extraits du CV

### 5.3 Les dictionnaires

Un dictionnaire stocke des donnees sous forme `cle -> valeur`.

Exemple:

```python
student = {
    "name": "Ali",
    "city": "Casablanca",
    "skills": ["python", "sql"]
}
```

Dans le projet, les dictionnaires sont essentiels pour:

- construire des payloads JSON
- manipuler des donnees intermediaires
- representer une offre scrapee avant de la sauver
- retourner des statistiques

Si tu comprends bien les dictionnaires, tu comprendras une grande partie du backend.

### 5.4 Les classes

Une classe est un plan.
Un objet est une instance concrete de ce plan.

Exemple:

```python
class Student:
    def __init__(self, name):
        self.name = name
```

Dans Django, les modeles sont des classes.

Exemple concret dans ce projet:

- `User`
- `StudentProfile`
- `CompanyProfile`
- `InternshipOffer`
- `Application`
- `Recommendation`

Ce qu'il faut comprendre:

- une classe regroupe des donnees et parfois des comportements
- un objet cree a partir de cette classe represente une vraie chose


## 6. Partie 2 - Django

Django est le framework backend.

Un framework est une structure qui te donne deja beaucoup de choses:

- gestion des routes
- connexion a la base de donnees
- systeme d'utilisateurs
- administration
- validation
- structure de projet

Dans ce projet, Django est organise avec des apps.

### 6.1 Les apps Django du projet

#### `users`

Responsabilites:

- comptes
- roles
- profils etudiants
- profils entreprises
- upload CV

#### `offers`

Responsabilites:

- offres de stage
- candidatures
- scraping

#### `ai`

Responsabilites:

- recommandations
- analyse du CV
- tendances
- lettre de motivation
- entretien

#### `core`

Responsabilites:

- configuration globale
- urls principales


## 7. Les models Django

Les models sont le coeur des donnees.

Un model Django est une classe Python qui represente une table en base de donnees.

### Exemples dans ce projet

- `User`: un utilisateur
- `StudentProfile`: profil etudiant
- `CompanyProfile`: profil entreprise
- `InternshipOffer`: offre
- `Application`: candidature
- `Recommendation`: score de recommandation

### Pourquoi c'est important

Quand tu comprends les models, tu comprends:

- quelles donnees existent
- comment elles sont liees
- ce que le projet sait stocker

### Relations importantes

#### `User` -> `StudentProfile`

Un utilisateur etudiant a un seul profil etudiant.

#### `User` -> `CompanyProfile`

Un utilisateur entreprise a un seul profil entreprise.

#### `CompanyProfile` -> `InternshipOffer`

Une entreprise peut avoir plusieurs offres.

#### `StudentProfile` -> `Application`

Un etudiant peut avoir plusieurs candidatures.

#### `InternshipOffer` -> `Application`

Une offre peut recevoir plusieurs candidatures.

#### `StudentProfile` -> `Recommendation`

Un etudiant peut avoir plusieurs recommandations.


## 8. Les serializers Django REST Framework

Un serializer sert a transformer des donnees.

Il fait 2 choses:

1. objet Python/Django -> JSON
2. JSON recu -> donnees validees

### Pourquoi c'est indispensable

Le frontend ne comprend pas les objets Django.
Il comprend surtout du JSON.

Donc il faut un pont entre les deux.

Ce pont, c'est le serializer.

### Exemple simple

Si une offre existe en base, le serializer permet de la transformer en JSON comme:

```json
{
  "id": 1,
  "title": "Stage Python",
  "location": "Casablanca"
}
```

### Dans le projet

Tu trouves des serializers dans:

- `backend/users/serializers.py`
- `backend/offers/serializers.py`
- `backend/ai/serializers.py`

### Ce qu'il faut comprendre

- un serializer choisit les champs exposes
- il peut valider les donnees entrantes
- il peut enrichir la reponse


## 9. Les views Django REST Framework

Une view est la logique d'un endpoint API.

En gros:

- la requete arrive
- la vue lit les donnees
- elle valide
- elle fait un traitement
- elle parle a la base
- elle retourne une reponse JSON

### Exemples de vues dans le projet

- lister les offres
- creer une offre
- postuler a une offre
- retirer une candidature
- recalculer les recommandations
- lancer le scraping Maroc

### Ce qu'il faut comprendre

Quand tu lis une view, pose-toi ces questions:

1. quelle route appelle cette vue ?
2. quelle methode HTTP est utilisee ?
3. qui a le droit d'y acceder ?
4. quelles donnees sont lues ?
5. que retourne la vue ?


## 10. Les urls Django

Les urls relient les routes HTTP aux views.

Exemple logique:

- `/api/offers/` -> liste des offres
- `/api/ai/recommendations/` -> recommandations
- `/api/users/me/` -> profil courant

### Ce qu'il faut comprendre

Les urls te disent:

- quel endpoint existe
- quel module le gere
- comment naviguer dans l'API

Si tu veux comprendre le projet, les urls sont une tres bonne carte.


## 11. Partie 3 - API, HTTP, JSON, JWT

Le frontend et le backend communiquent via une API.

### 11.1 HTTP

HTTP est le protocole de communication web.

Les methodes principales ici:

- `GET`: lire des donnees
- `POST`: creer ou declencher une action
- `PATCH`: modifier partiellement
- `DELETE`: supprimer

### 11.2 JSON

JSON est le format d'echange.

Exemple:

```json
{
  "title": "Stage Data Analyst",
  "location": "Rabat"
}
```

Le frontend envoie du JSON au backend.
Le backend repond en JSON au frontend.

### 11.3 JWT

JWT = JSON Web Token.

C'est le systeme d'authentification du projet.

Quand un utilisateur se connecte:

- il recoit un `access token`
- il recoit un `refresh token`

Le frontend garde ces tokens et les envoie au backend.

### Pourquoi c'est utile

Cela permet au backend de savoir:

- qui fait la requete
- si la personne est connectee
- si c'est un etudiant ou une entreprise

### Dans ce projet

Le refresh automatique est gere par Axios dans:

- `frontend/src/services/api.ts`


## 12. Partie 4 - React

React est le framework frontend.

Il sert a construire l'interface sous forme de composants.

### 12.1 Un composant

Un composant est un bloc d'interface reutilisable.

Exemple:

- page login
- navbar
- carte d'offre
- formulaire profil

### 12.2 `useState`

`useState` sert a stocker l'etat local d'un composant.

Exemple:

- le contenu d'un champ
- la liste des offres
- un boolen de chargement

### 12.3 `useEffect`

`useEffect` sert a declencher une action quand le composant s'affiche ou quand une dependance change.

Exemple:

- charger les offres au demarrage
- appeler une API quand l'utilisateur change

### 12.4 Routing

Le routing sert a gerer les pages.

Dans ce projet, les routes sont declarees dans:

- `frontend/src/App.tsx`

Exemples:

- `/login`
- `/register`
- `/offers`
- `/dashboard`
- `/recommendations`


## 13. Partie 5 - TypeScript

Le frontend n'utilise pas seulement JavaScript, mais TypeScript.

TypeScript ajoute des types.

### Pourquoi c'est utile

Ca aide a:

- detecter des erreurs plus tot
- mieux comprendre la forme des donnees
- mieux relier frontend et backend

### Ce qu'il faut comprendre au debut

Tu n'as pas besoin de maitriser tout TypeScript.

Tu dois d'abord comprendre:

- `interface`
- `type`
- types primitifs: `string`, `number`, `boolean`
- tableaux: `string[]`
- optionnel: `field?: string`


## 14. Partie 6 - La logique metier du projet

### 14.1 Cote etudiant

Un etudiant peut:

- s'inscrire
- se connecter
- remplir son profil
- uploader son CV
- voir des offres
- voir ses recommandations
- postuler
- retirer une candidature

### 14.2 Cote entreprise

Une entreprise peut:

- s'inscrire
- se connecter
- creer une offre
- voir ses offres
- voir les candidatures recues
- changer le statut d'une candidature

### 14.3 Cote admin

Un admin peut:

- acceder a l'admin Django
- declencher le scraping
- voir les statistiques IA


## 15. Partie 7 - La partie IA du projet

Beaucoup de gens entendent "IA" et pensent a quelque chose de tres mysterieux.
Ici, il faut etre clair:

Le projet utilise une IA au sens pratique:

- traitement de texte
- extraction de competences
- similarite entre CV et offres
- parfois Gemini si une cle API est disponible

### 15.1 Etape 1: lire le CV

Le systeme lit:

- PDF avec `pdfplumber`
- DOCX avec `python-docx`

### 15.2 Etape 2: extraire du texte

Le texte du CV est converti en une forme exploitable.

### 15.3 Etape 3: normaliser

Normaliser veut dire:

- mettre en minuscules
- nettoyer les caracteres inutiles
- harmoniser certains mots

Exemple:

- `JS` -> `javascript`
- `Nodejs` -> `node.js`

### 15.4 Etape 4: extraire des competences

Le systeme cherche des competences dans le texte:

- Python
- Django
- React
- SQL
- etc.

### 15.5 Etape 5: comparer CV et offres

Le systeme construit une representation textuelle du CV et des offres.

Puis il calcule une proximite.

### 15.6 Etape 6: score final

Le score final melange:

- similarite semantique
- overlap de competences
- bonus contextuel

Exemples de bonus:

- offre de type stage
- offre au Maroc
- etudiant junior
- offre remuneree


## 16. TF-IDF et similarite cosinus

Ce sont les notions IA les plus importantes a comprendre pour ce projet.

### 16.1 TF-IDF

TF-IDF est une technique classique de NLP.

Le but:

- transformer du texte en representation numerique
- donner plus de poids aux mots importants
- donner moins de poids aux mots trop frequents

En version tres simple:

- si un mot apparait souvent dans un document, il est important pour ce document
- mais s'il apparait partout, il est moins discriminant

### 16.2 Similarite cosinus

Une fois que le CV et l'offre sont transformes en vecteurs, on mesure leur proximite.

La similarite cosinus dit:

- proche de `1` = tres similaire
- proche de `0` = peu similaire

### Ce que tu dois retenir

Le moteur ne "pense" pas comme un humain.
Il mesure mathematiquement la proximite entre contenus textuels.


## 17. Partie 8 - Le scraping

Le scraping sert a recuperer des offres depuis le web.

### Etapes du scraping

1. envoyer une requete HTTP
2. recuperer le HTML
3. analyser ce HTML
4. trouver les blocs utiles
5. extraire les informations
6. sauver les offres en base

### Bibliotheques utilisees

- `requests`
- `BeautifulSoup`

### Sources visees dans le projet

- Rekrute
- Emploi.ma
- fallback distant
- fallback local si reseau indisponible

### Pourquoi un fallback existe

Parce qu'en pratique:

- le reseau peut etre bloque
- le site peut changer
- le DNS peut echouer
- le scraping peut ne rien renvoyer

Donc le projet prevoit un comportement de secours.


## 18. Partie 9 - Structure des fichiers a lire

Si tu veux comprendre le projet, lis les fichiers dans cet ordre.

### Backend

1. `backend/core/settings.py`
2. `backend/core/urls.py`
3. `backend/users/models.py`
4. `backend/offers/models.py`
5. `backend/ai/models.py`
6. `backend/users/serializers.py`
7. `backend/offers/serializers.py`
8. `backend/ai/serializers.py`
9. `backend/users/views.py`
10. `backend/offers/views.py`
11. `backend/ai/views.py`
12. `backend/ai/services.py`
13. `backend/offers/scraper.py`

### Frontend

1. `frontend/src/main.tsx`
2. `frontend/src/App.tsx`
3. `frontend/src/contexts/AuthContext.tsx`
4. `frontend/src/services/api.ts`
5. `frontend/src/pages/Offers.tsx`
6. `frontend/src/pages/Profile.tsx`
7. `frontend/src/pages/Recommendations.tsx`
8. `frontend/src/pages/MyApplications.tsx`
9. `frontend/src/pages/MyOffers.tsx`


## 19. Partie 10 - Comment lire un fichier sans te perdre

Quand tu ouvres un fichier, pose-toi toujours ces questions:

1. ce fichier sert a quoi ?
2. quelles donnees il manipule ?
3. qui l'appelle ?
4. qu'est-ce qu'il renvoie ou affiche ?
5. quel est le flux entree -> traitement -> sortie ?

### Exemple pour une view backend

- entree: requete HTTP
- traitement: lecture, validation, logique
- sortie: JSON

### Exemple pour une page React

- entree: etat, props, reponse API
- traitement: logique React
- sortie: interface visible


## 20. Partie 11 - Ce que tu dois apprendre en premier, sans te disperser

Si tu veux devenir autonome, voici l'ordre ideal.

### Niveau 1 - indispensable

1. fonctions Python
2. listes Python
3. dictionnaires Python
4. classes Python
5. model Django
6. serializer Django
7. view Django
8. url Django
9. HTTP
10. JSON
11. JWT
12. composant React
13. `useState`
14. `useEffect`
15. routing React

### Niveau 2 - important

16. relations entre models
17. permissions Django
18. Axios
19. contexte React
20. TypeScript interfaces
21. requetes API protegees
22. pagination
23. filtres

### Niveau 3 - plus avance

24. TF-IDF
25. similarite cosinus
26. extraction heuristique de competences
27. parsing HTML
28. scraping robuste
29. architecture logicielle
30. securite et prod


## 21. Partie 12 - Ce que tu dois absolument retenir

Voici les idees les plus importantes.

### Idee 1

Le backend est le cerveau.
Le frontend est la vitrine.

### Idee 2

Les models disent quelles donnees existent.

### Idee 3

Les serializers convertissent les objets en JSON et valident les donnees.

### Idee 4

Les views contiennent les actions metier.

### Idee 5

Les urls relient les routes a la logique.

### Idee 6

React affiche ce que le backend renvoie.

### Idee 7

L'IA du projet repose surtout sur:

- texte
- competences
- similarite
- scoring

### Idee 8

Le scraping ajoute des offres externes a la plateforme.


## 22. Partie 13 - Ce que "comprendre le projet" veut vraiment dire

Tu n'as pas besoin de connaitre chaque detail de chaque bibliotheque pour comprendre le projet.

Comprendre le projet veut dire:

- savoir ce que fait chaque partie
- savoir comment les parties communiquent
- savoir ou chercher quand il y a un bug
- savoir lire une route de bout en bout
- savoir suivre une donnee depuis le frontend jusqu'a la base

Exemple:

- l'etudiant clique sur "postuler"
- React envoie une requete
- Django recoit la requete
- la view valide
- la candidature est creee
- le backend renvoie du JSON
- le frontend met a jour l'affichage

Si tu sais raconter ce genre de flux, alors tu comprends deja beaucoup.


## 23. Partie 14 - Comment passer de debutant a expert

Un expert n'est pas quelqu'un qui memorise tout.
Un expert est quelqu'un qui:

- sait decomposer un probleme
- comprend les flux
- sait ou chercher
- sait lire le code sans paniquer
- sait relier la theorie et le concret

### Etape 1

Comprendre les bases Python.

### Etape 2

Comprendre les models et les vues Django.

### Etape 3

Comprendre comment React appelle le backend.

### Etape 4

Comprendre le moteur de recommandation.

### Etape 5

Comprendre comment une fonctionnalite complete traverse tout le projet.

### Etape 6

Modifier le projet toi-meme sur de petites taches.

### Etape 7

Apprendre a debugger.

### Etape 8

Ameliorer l'architecture, les tests, la securite et la qualite.


## 24. Partie 15 - La meilleure maniere d'utiliser ce document

Ne lis pas ce guide comme un roman.

Utilise-le comme un plan de travail.

### Methode conseillee

1. lire une section
2. ouvrir les fichiers correspondants
3. essayer de reconnaitre la notion dans le code
4. reformuler avec tes propres mots
5. revenir sur les points flous

### Exemple

Si tu lis la section "serializers":

- ouvre `backend/offers/serializers.py`
- repere la classe serializer
- regarde les champs
- regarde la validation
- essaye d'expliquer a voix haute ce que fait le fichier


## 25. Conclusion

Oui, ce projet a ete beaucoup aide par l'IA.
Mais maintenant, il peut devenir ton vrai terrain d'apprentissage.

Tu n'es pas oblige de tout comprendre d'un coup.
Tu dois juste avancer dans le bon ordre.

Le plus important:

- Python pour lire la logique
- Django pour comprendre le backend
- React pour comprendre l'interface
- API pour comprendre la communication
- IA pour comprendre les recommandations
- scraping pour comprendre l'import des offres

Si tu maitrises bien ces blocs, tu ne seras plus passif devant ce projet.
Tu pourras l'expliquer, le modifier, le corriger et l'ameliorer toi-meme.
