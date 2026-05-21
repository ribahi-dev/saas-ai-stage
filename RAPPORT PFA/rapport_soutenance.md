# 🎓 Rapport d'Ingénierie & Architecture : SaaS AI Stage
**Document de préparation à la soutenance**

Ce document est conçu pour vous donner une vision claire, technique et professionnelle de votre projet. Lisez-le attentivement : il vous donnera les mots exacts à utiliser devant votre jury pour prouver que vous maîtrisez l'application de bout en bout.

---

## 1. Vue d'Ensemble du Projet (Elevator Pitch)

**Le problème :** Les étudiants peinent à trouver des stages adaptés à leurs compétences réelles, et les entreprises reçoivent trop de candidatures non qualifiées.
**La solution :** Une plateforme SaaS intelligente (SaaS AI Stage) qui agit comme un entremetteur algorithmique. 

L'application ne se contente pas d'afficher des offres : elle **lit les CV des étudiants**, en **extrait les compétences clés**, et utilise un **moteur de Machine Learning (NLP)** pour calculer un score de matching avec les offres disponibles sur le marché (publiées par les entreprises ou récupérées via notre Scraper web).

---

## 2. Architecture Technique Globale

Le projet suit une architecture **"Headless"** ou **"Découplée"**. C'est une excellente pratique de l'industrie car elle sépare la logique métier de l'interface visuelle.

> [!TIP]
> **Argument pour le jury :** *"Nous avons choisi une architecture découplée (Frontend React séparé du Backend Django) pour garantir la scalabilité du projet. Si demain nous voulons créer une application mobile iOS/Android, notre Backend restera exactement le même, il suffira de consommer notre API."*

### 🛠️ La Stack Technologique :
- **Backend (API REST) :** Python & Django REST Framework (DRF)
- **Frontend (UI/UX) :** React.js, TypeScript, Tailwind CSS, Vite
- **Base de données :** PostgreSQL (Choisie pour sa robustesse relationnelle et sa scalabilité)
- **Intelligence Artificielle :** Scikit-learn (Machine Learning), `pdfplumber` (Extraction de texte), Google Generative AI (Gemini) pour l'aide contextuelle.
- **Sécurité :** Authentification par Token JWT (JSON Web Tokens).

---

## 3. Le Modèle de Données (Base de données PostgreSQL)

Votre base de données est le cœur du système. Voici comment elle est structurée (vous pouvez montrer ça sous forme de diagramme Entité-Relation au jury) :

1. **`users_user`** : La table d'authentification principale gérée par Django. Gère les emails, mots de passe hashés et rôles (`student`, `company`, `admin`).
2. **Profils étendus (Héritage) :**
   - **`users_studentprofile`** : Lié à User (1:1). Stocke le CV, la bio, et surtout le champ `extracted_skills` (Compétences extraites par l'IA).
   - **`users_companyprofile`** : Lié à User (1:1). Stocke le nom de l'entreprise, le logo, le secteur.
3. **`offers_internshipoffer`** : Les offres publiées ou scrapées. Contient un champ crucial : `required_skills` (Le texte qui sera comparé aux CV).
4. **`offers_application`** : La table de jointure "Candidature". Relie un Étudiant à une Offre, avec un champ `status` (Pending, Accepted, Rejected).
5. **`ai_recommendation`** : Stocke le score de matching pré-calculé entre un `Student` et une `Offer` pour un affichage rapide dans le Dashboard.

---

## 4. Le Moteur d'Intelligence Artificielle (NLP)

C'est la pièce maîtresse technique du projet. Comment l'application comprend-elle un CV et le compare-t-elle à une offre ?

### Étape 1 : Extraction (Parsing)
Lorsqu'un étudiant upload son CV, le backend utilise `pdfplumber` pour extraire le texte brut du fichier PDF.

### Étape 2 : Nettoyage et Normalisation (Preprocessing)
Le texte extrait est souvent chaotique. L'algorithme le nettoie (passage en minuscules, suppression de la ponctuation, uniformisation des termes comme "JS" -> "javascript").

### Étape 3 : Le Matching via TF-IDF & Cosine Similarity
> [!IMPORTANT]
> **C'est ce que vous devez expliquer au jury.**

Nous utilisons deux concepts mathématiques de base du *Natural Language Processing* (NLP) :
- **TF-IDF (Term Frequency-Inverse Document Frequency) :** C'est un algorithme qui vectorise le texte. Il donne beaucoup de "poids" aux mots qui sont rares dans le vocabulaire global mais très fréquents dans le CV (ex: "React", "Django"). Les mots communs ("le", "de", "et") ont un poids de 0.
- **Similarité Cosinus (Cosine Similarity) :** Une fois le CV transformé en vecteur mathématique, et l'Offre transformée en vecteur, l'algorithme calcule l'angle géométrique (le cosinus) entre ces deux vecteurs. 
  - Cosinus = 1 : Les textes sont identiques (Match parfait à 100%).
  - Cosinus = 0 : Aucun mot en commun (Match à 0%).

### Étape 4 : Le Score Hybride
Le score NLP brut n'est pas suffisant. L'application calcule un **Score Global** en ajoutant des "Bonus" : 
- L'étudiant veut travailler à Casablanca et l'offre est à Casablanca ? *+ Bonus de localisation.*
- L'offre correspond exactement au type cherché (Stage) ? *+ Bonus de type.*

---

## 5. Le Moteur de Scraping (Data Mining)

Pour que la plateforme ne soit pas vide à son lancement (problème de l'œuf et de la poule), nous avons développé un **Scraper Bot** en Python (avec `requests` et `BeautifulSoup`).

1. **Extraction Web :** L'admin lance une commande (`python manage.py scrape_morocco_offers`).
2. Le scraper cible des sites d'emploi publics marocains (Rekrute, Emploi.ma).
3. Il télécharge le code HTML des pages de résultats.
4. Il parse le HTML pour trouver les balises contenant le titre, l'entreprise et la description de l'offre.
5. Il sauvegarde l'offre automatiquement dans notre base de données PostgreSQL.

---

## 6. L'Authentification (JWT)

Le jury demandera sûrement comment est sécurisée l'API.

- Nous utilisons **JWT (JSON Web Tokens)**.
- Quand un utilisateur se connecte, le Backend Django vérifie le mot de passe et renvoie un Token crypté au Frontend React.
- Pour chaque action (ex: postuler à une offre), React attache ce Token dans le "Header" de la requête HTTP (`Authorization: Bearer <token>`).
- Le Backend décrypte le Token, sait exactement qui fait la demande, et autorise (ou refuse) l'action. C'est sécurisé et *stateless* (le serveur n'a pas besoin de mémoriser les sessions).

---

## 7. Flux de l'Application (User Journey)

Voici comment résumer le parcours utilisateur type (Happy Path) :

**Pour l'Étudiant :**
1. Création de compte (géré par `/api/users/register/`).
2. Upload du CV en PDF. Le Backend le parse instantanément de manière asynchrone (ou synchrone selon l'implémentation finale) et extrait les compétences (`/api/users/me/cv/`).
3. Le Moteur IA génère les recommandations (`/api/ai/recommendations/`).
4. L'étudiant voit un Dashboard avec des offres triées par "Score de compatibilité".
5. Il clique sur "Postuler" (`POST /api/offers/<id>/apply/`).

**Pour l'Entreprise :**
1. Elle se connecte et publie une nouvelle Offre via un formulaire React (`POST /api/offers/`).
2. Elle accède à son tableau de bord (`GET /api/offers/received-applications/`).
3. Elle voit les candidatures (avec le CV de l'étudiant attaché) et change le statut en "Accepted" ou "Rejected".

---

## 💡 Conseils pour la soutenance

1. **Ne lisez pas vos notes :** Parlez avec passion de l'architecture. Dites "Nous avons choisi Django car...", "React nous permet de...".
2. **Soyez honnête sur l'IA :** Si on vous demande si vous avez créé une IA, répondez : *"Nous n'avons pas entraîné de modèle Deep Learning (Réseau de neurones) à partir de zéro, cela n'aurait pas de sens pour du texte. Nous avons appliqué des modèles mathématiques de Machine Learning (TF-IDF) et du NLP pour la similarité sémantique, couplés à des API LLM génératives pour l'assistance contextuelle."*
3. **Mettez en avant le Scraping :** Le fait que la plateforme puisse s'auto-alimenter en données est une énorme force technique et commerciale.
