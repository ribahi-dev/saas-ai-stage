-- ============================================================
-- PLATEFORME INTELLIGENTE DE RECOMMANDATION DE STAGES
-- Schéma MySQL — Compatible MySQL Workbench & MySQL 8.0+
-- ============================================================
-- Usage MySQL Workbench :
--   1. File → Open SQL Script → sélectionner ce fichier
--   2. Database → Forward Engineer  OU  Exécuter le script (⚡)
--   3. Ou : Menu Server → Data Import → Import from Self-Contained File
-- ============================================================

-- Créer et sélectionner la base de données
CREATE DATABASE IF NOT EXISTS plateforme_stages_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE plateforme_stages_db;

-- ============================================================
-- SECTION 1 — UTILISATEURS (App Django : users)
-- ============================================================

-- ------------------------------------------------------------
-- Table : users_user
-- Rôle  : Compte de base pour tout utilisateur.
--         Hérite du modèle AbstractUser Django.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users_user (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,
    password            VARCHAR(128)    NOT NULL COMMENT 'Hash PBKDF2/bcrypt géré par Django. Jamais en clair.',
    last_login          DATETIME        NULL,
    is_superuser        TINYINT(1)      NOT NULL DEFAULT 0,
    username            VARCHAR(150)    NOT NULL COMMENT 'Nom d utilisateur unique (login)',
    first_name          VARCHAR(150)    NOT NULL DEFAULT '',
    last_name           VARCHAR(150)    NOT NULL DEFAULT '',
    email               VARCHAR(254)    NOT NULL DEFAULT '',
    is_staff            TINYINT(1)      NOT NULL DEFAULT 0 COMMENT 'Accès à /admin/',
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    date_joined         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Champ métier : distingue ÉTUDIANT / ENTREPRISE / ADMIN
    role                VARCHAR(10)     NOT NULL DEFAULT 'student'
                            COMMENT 'Valeurs : student | company | admin',

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_user_username (username),
    CONSTRAINT chk_user_role CHECK (role IN ('student', 'company', 'admin')),

    INDEX idx_users_user_role  (role),
    INDEX idx_users_user_email (email)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Compte utilisateur unifié — étudiant, entreprise, admin.';


-- ------------------------------------------------------------
-- Table : users_studentprofile
-- Rôle  : Profil détaillé de l'étudiant.
--         OneToOne avec users_user (role=''student'').
--         Colonnes NLP remplies en Phase 4.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users_studentprofile (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,

    -- Lien OneToOne vers le compte utilisateur
    user_id             BIGINT          NOT NULL UNIQUE
                            COMMENT 'FK OneToOne vers users_user',

    -- Informations personnelles
    bio                 TEXT            NULL,
    phone               VARCHAR(20)     NULL,
    linkedin_url        VARCHAR(200)    NULL,

    -- Informations académiques
    university          VARCHAR(200)    NULL   COMMENT 'Ex: ENSIAS, ENSA Casablanca',
    field_of_study      VARCHAR(200)    NULL   COMMENT 'Ex: Génie Logiciel, Data Science',
    graduation_year     SMALLINT        NULL
                            COMMENT 'Année de diplôme (2000-2035)',

    -- Fichier CV
    cv_file             VARCHAR(255)    NULL   COMMENT 'Chemin relatif : cvs/nom_cv.pdf',

    -- ── Colonnes NLP — Remplies en Phase 4 ───────────────────
    cv_text_extracted   LONGTEXT        NULL
                            COMMENT 'Phase 4 : Texte brut extrait du PDF via pdfplumber',
    cv_vector_json      LONGTEXT        NULL
                            COMMENT 'Phase 4 : Vecteur TF-IDF sérialisé en JSON',
    -- ─────────────────────────────────────────────────────────

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_studentprofile_user FOREIGN KEY (user_id)
        REFERENCES users_user(id) ON DELETE CASCADE,
    INDEX idx_studentprofile_user (user_id)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Profil étudiant avec données NLP pour le moteur de recommandation.';


-- ------------------------------------------------------------
-- Table : users_companyprofile
-- Rôle  : Profil de l'entreprise qui publie des offres.
--         OneToOne avec users_user (role=''company'').
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users_companyprofile (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,

    -- Lien OneToOne vers le compte utilisateur
    user_id             BIGINT          NOT NULL UNIQUE,

    -- Informations entreprise
    company_name        VARCHAR(200)    NOT NULL,
    description         TEXT            NULL,
    website             VARCHAR(200)    NULL,
    industry            VARCHAR(100)    NULL   COMMENT 'Ex: FinTech, E-commerce, Santé',
    city                VARCHAR(100)    NULL,
    country             VARCHAR(100)    NOT NULL DEFAULT 'Maroc',
    logo                VARCHAR(255)    NULL   COMMENT 'Chemin vers image logo uploadée',

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_companyprofile_user FOREIGN KEY (user_id)
        REFERENCES users_user(id) ON DELETE CASCADE,
    INDEX idx_companyprofile_user (user_id)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Profil entreprise — publie des offres de stage.';


-- ============================================================
-- SECTION 2 — OFFRES DE STAGE (App Django : offers)
-- ============================================================

-- ------------------------------------------------------------
-- Table : offers_internshipoffer
-- Rôle  : Offre de stage publiée par une entreprise.
--         required_skills est le texte analysé par TF-IDF.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS offers_internshipoffer (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,

    -- Lien vers l'entreprise publiante
    company_id          BIGINT          NOT NULL,

    -- Contenu de l'offre
    title               VARCHAR(200)    NOT NULL,
    description         TEXT            NOT NULL,

    -- ── Champ clé pour le moteur NLP ─────────────────────────
    required_skills     TEXT            NOT NULL
                            COMMENT 'Phase 4 : Texte libre analysé par TF-IDF. Ex: Python Django REST API',
    -- ─────────────────────────────────────────────────────────

    -- Logistique du stage
    location            VARCHAR(200)    NULL COMMENT 'Ex: Casablanca, Remote, Rabat',
    duration_months     TINYINT         NULL COMMENT 'Durée en mois (1-12)',
    is_paid             TINYINT(1)      NOT NULL DEFAULT 0,
    salary              DECIMAL(8, 2)   NULL COMMENT 'Montant mensuel si rémunéré',

    -- Statut et dates
    is_active           TINYINT(1)      NOT NULL DEFAULT 1 COMMENT '1=publiée, 0=archivée',
    deadline            DATE            NULL COMMENT 'Date limite de candidature',

    -- ── NLP pré-calculé (Phase 4) ─────────────────────────────
    offer_vector_json   LONGTEXT        NULL
                            COMMENT 'Phase 4 : Vecteur TF-IDF pré-calculé pour performance',
    -- ─────────────────────────────────────────────────────────

    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    CONSTRAINT fk_offer_company FOREIGN KEY (company_id)
        REFERENCES users_companyprofile(id) ON DELETE CASCADE,
    CONSTRAINT chk_offer_duration CHECK (duration_months BETWEEN 1 AND 12),
    CONSTRAINT chk_offer_salary   CHECK (salary >= 0),

    INDEX idx_offer_company   (company_id),
    INDEX idx_offer_active    (is_active),
    INDEX idx_offer_deadline  (deadline)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Offres de stage. required_skills alimente le moteur TF-IDF.';


-- ------------------------------------------------------------
-- Table : offers_application
-- Rôle  : Candidature d'un étudiant à une offre de stage.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS offers_application (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,

    -- Les deux parties de la candidature
    student_id          BIGINT          NOT NULL,
    offer_id            BIGINT          NOT NULL,

    -- Statut géré par l'entreprise
    status              VARCHAR(20)     NOT NULL DEFAULT 'pending'
                            COMMENT 'pending | accepted | rejected | withdrawn',
    cover_letter        TEXT            NULL,
    applied_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Un étudiant ne postule qu'une seule fois par offre
    UNIQUE KEY uq_application (student_id, offer_id),

    CONSTRAINT fk_application_student FOREIGN KEY (student_id)
        REFERENCES users_studentprofile(id) ON DELETE CASCADE,
    CONSTRAINT fk_application_offer FOREIGN KEY (offer_id)
        REFERENCES offers_internshipoffer(id) ON DELETE CASCADE,
    CONSTRAINT chk_application_status
        CHECK (status IN ('pending', 'accepted', 'rejected', 'withdrawn')),

    INDEX idx_application_student (student_id),
    INDEX idx_application_offer   (offer_id),
    INDEX idx_application_status  (status)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Candidature étudiant-offre. Statut géré par l entreprise.';


-- ============================================================
-- SECTION 3 — MOTEUR IA (App Django : ai)
-- ============================================================

-- ------------------------------------------------------------
-- Table : ai_recommendation
-- Rôle  : Cache des scores de similarité cosinus.
--         Calculé par le moteur TF-IDF (Phase 4).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_recommendation (
    id                  BIGINT          NOT NULL AUTO_INCREMENT,

    -- La paire (étudiant ↔ offre) scorée
    student_id          BIGINT          NOT NULL,
    offer_id            BIGINT          NOT NULL,

    -- Score de similarité cosinus [0.0 — 1.0]
    score               FLOAT           NOT NULL DEFAULT 0.0
                            COMMENT 'Similarité cosinus TF-IDF. 1.0=parfait, 0.0=aucun match',

    -- Horodatage du dernier calcul
    computed_at         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                            ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Un seul score par paire
    UNIQUE KEY uq_recommendation (student_id, offer_id),

    CONSTRAINT fk_rec_student FOREIGN KEY (student_id)
        REFERENCES users_studentprofile(id) ON DELETE CASCADE,
    CONSTRAINT fk_rec_offer FOREIGN KEY (offer_id)
        REFERENCES offers_internshipoffer(id) ON DELETE CASCADE,
    CONSTRAINT chk_rec_score CHECK (score >= 0.0 AND score <= 1.0),

    -- Index composé : permet de trier par score DESC rapidement
    INDEX idx_rec_student_score (student_id, score DESC)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Cache des scores TF-IDF/Cosinus. Mis à jour à chaque upload de CV.';


-- ============================================================
-- SECTION 4 — DONNÉES DE TEST (Seed Data)
-- Décommenter pour peupler la DB en développement
-- ============================================================

/*
-- Compte admin
INSERT INTO users_user (username, email, password, role, is_staff, is_superuser, is_active)
VALUES ('admin', 'admin@plateforme.ma', 'pbkdf2_sha256$...hash...', 'admin', 1, 1, 1);

-- Compte entreprise
INSERT INTO users_user (username, email, password, role, is_active)
VALUES ('techcorp_rh', 'rh@techcorp.ma', 'pbkdf2_sha256$...hash...', 'company', 1);

INSERT INTO users_companyprofile (user_id, company_name, industry, city, country)
VALUES (2, 'TechCorp Maroc', 'FinTech', 'Casablanca', 'Maroc');

-- Offre de stage
INSERT INTO offers_internshipoffer (company_id, title, description, required_skills, duration_months, is_active)
VALUES (1, 'Stage Développeur Backend Python',
        'Développez des APIs REST performantes au sein de notre équipe FinTech.',
        'Python Django REST API PostgreSQL MySQL Docker Git CI/CD Agile',
        6, 1);

-- Compte étudiant
INSERT INTO users_user (username, email, password, role, is_active)
VALUES ('elmehdaoui', 'elmeh@etudiant.ma', 'pbkdf2_sha256$...hash...', 'student', 1);

INSERT INTO users_studentprofile (user_id, university, field_of_study, graduation_year)
VALUES (3, 'ENSIAS', 'Génie Logiciel', 2026);
*/

-- ============================================================
-- FIN DU SCHÉMA
-- ============================================================
-- Résumé :
--   1. users_user              → Comptes (student | company | admin)
--   2. users_studentprofile    → Profils étudiants + données NLP (CV)
--   3. users_companyprofile    → Profils entreprises
--   4. offers_internshipoffer  → Offres de stage
--   5. offers_application      → Candidatures
--   6. ai_recommendation       → Scores TF-IDF/Cosinus (cache IA)
-- ============================================================

SELECT 'Schema plateforme_stages_db cree avec succes !' AS message;
