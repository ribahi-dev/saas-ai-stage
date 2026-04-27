"""
users/models.py — Modèles Utilisateur, StudentProfile, CompanyProfile

Architecture "Type-based User Model" :
  - Un seul modèle User (role = student | company | admin)
  - Deux profils via OneToOneField : StudentProfile et CompanyProfile
  - Les profils sont créés automatiquement par RegisterSerializer
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# ─────────────────────────────────────────────────────────────────────────────
# 1. USER — Compte de base pour tout utilisateur
# ─────────────────────────────────────────────────────────────────────────────

class User(AbstractUser):
    """
    Modèle utilisateur étendu.
    Hérite de AbstractUser → on garde tout (username, email, password,
    is_staff, is_active, etc.) et on AJOUTE nos champs métier.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Étudiant'
        COMPANY = 'company', 'Entreprise'
        ADMIN   = 'admin',   'Administrateur'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Rôle"
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_company(self):
        return self.role == self.Role.COMPANY


# ─────────────────────────────────────────────────────────────────────────────
# 2. STUDENT PROFILE — Extension OneToOne du compte étudiant
# ─────────────────────────────────────────────────────────────────────────────

class StudentProfile(models.Model):
    """
    Profil détaillé de l'étudiant.
    Les champs NLP (cv_text_extracted, cv_vector_json) sont remplis
    automatiquement lors de l'upload du CV (Phase 4 — moteur TF-IDF).
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': User.Role.STUDENT},
    )

    # ── Informations personnelles ──────────────────────────────
    bio          = models.TextField(blank=True, null=True)
    phone        = models.CharField(max_length=20, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    # ── Informations académiques ───────────────────────────────
    university      = models.CharField(max_length=200, blank=True, null=True,
                                       verbose_name="Université / École")
    field_of_study  = models.CharField(max_length=200, blank=True, null=True,
                                       verbose_name="Filière")
    graduation_year = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(2000), MaxValueValidator(2035)],
        verbose_name="Année de diplôme"
    )

    # ── Fichier CV ─────────────────────────────────────────────
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True,
                               verbose_name="CV (PDF)")

    # ── Champs NLP — Remplis en Phase 4 ───────────────────────
    cv_text_extracted = models.TextField(blank=True, null=True,
                                         verbose_name="Texte extrait du CV")
    cv_vector_json    = models.TextField(blank=True, null=True,
                                         verbose_name="Vecteur TF-IDF (JSON)")
    
    # ── Champs extraits par l'IA (Gemini) ──────────────────────
    extracted_skills = models.JSONField(blank=True, null=True, default=list, verbose_name="Compétences extraites par l'IA")
    experience_level = models.CharField(max_length=50, blank=True, null=True, default="Junior", verbose_name="Niveau d'expérience")
    projects = models.JSONField(blank=True, null=True, default=list, verbose_name="Projets extraits")
    target_job_titles = models.JSONField(blank=True, null=True, default=list, verbose_name="Intitules vises")
    preferred_locations = models.JSONField(blank=True, null=True, default=list, verbose_name="Villes preferees")
    preferred_offer_types = models.JSONField(blank=True, null=True, default=list, verbose_name="Types d'offres preferes")
    remote_ok = models.BooleanField(default=True, verbose_name="Accepte le remote")
    expected_salary = models.PositiveIntegerField(blank=True, null=True, verbose_name="Salaire vise (MAD)")

    # ── Timestamps ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Étudiant"
        verbose_name_plural = "Profils Étudiants"

    def __str__(self):
        return f"Profil de {self.user.username}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. COMPANY PROFILE — Extension OneToOne du compte entreprise
# ─────────────────────────────────────────────────────────────────────────────

class CompanyProfile(models.Model):
    """
    Profil de l'entreprise qui publie des offres de stage.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile',
        limit_choices_to={'role': User.Role.COMPANY},
    )

    # ── Infos entreprise ──────────────────────────────────────
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    description  = models.TextField(blank=True, null=True)
    website      = models.URLField(blank=True, null=True)
    industry     = models.CharField(max_length=100, blank=True, null=True,
                                    verbose_name="Secteur d'activité")
    city         = models.CharField(max_length=100, blank=True, null=True,
                                    verbose_name="Ville")
    country      = models.CharField(max_length=100, default='Maroc')
    logo         = models.ImageField(upload_to='logos/', blank=True, null=True)

    # ── Timestamps ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil Entreprise"
        verbose_name_plural = "Profils Entreprises"

    def __str__(self):
        return self.company_name
