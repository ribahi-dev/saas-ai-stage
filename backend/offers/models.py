"""
offers/models.py — Offres de Stage et Candidatures

Deux modèles :
  - InternshipOffer  : Offre publiée par une entreprise
  - Application      : Candidature d'un étudiant à une offre
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import StudentProfile, CompanyProfile


# ─────────────────────────────────────────────────────────────────────────────
# 1. INTERNSHIP OFFER — Offre de stage
# ─────────────────────────────────────────────────────────────────────────────

class InternshipOffer(models.Model):
    """
    Offre de stage publiée par une entreprise.
    Le champ `required_skills` est le texte brut analysé par le moteur TF-IDF
    pour calculer la similarité avec les CVs des étudiants.
    """

    class Status(models.TextChoices):
        ACTIVE   = 'active',   'Active'
        PAUSED   = 'paused',   'En pause'
        ARCHIVED = 'archived', 'Archivée'

    class OfferType(models.TextChoices):
        STAGE     = 'stage',     'Stage'
        EMPLOI    = 'emploi',    'Emploi (CDI/CDD)'
        FREELANCE = 'freelance', 'Freelance'

    # ── Liens ─────────────────────────────────────────────────
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name="Entreprise"
    )

    # ── Contenu de l'offre ────────────────────────────────────
    title       = models.CharField(max_length=200, verbose_name="Titre du poste")
    offer_type  = models.CharField(
        max_length=20, choices=OfferType.choices, default=OfferType.STAGE,
        verbose_name="Type d'offre"
    )
    description = models.TextField(verbose_name="Description détaillée")

    # ── Champ clé pour le moteur NLP ──────────────────────────
    required_skills = models.TextField(
        verbose_name="Compétences requises",
        help_text="Texte libre analysé par TF-IDF. Ex: Python Django REST API Git Docker"
    )

    # ── Logistique ────────────────────────────────────────────
    location        = models.CharField(max_length=200, blank=True, null=True,
                                       verbose_name="Lieu (ville / remote)")
    duration_months = models.PositiveSmallIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Durée (mois)"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Stage rémunéré ?")
    salary  = models.DecimalField(
        max_digits=8, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(0)],
        verbose_name="Rémunération mensuelle (MAD)"
    )

    # ── Statut & Dates ────────────────────────────────────────
    status   = models.CharField(max_length=10, choices=Status.choices,
                                default=Status.ACTIVE, verbose_name="Statut")
    deadline = models.DateField(blank=True, null=True,
                                verbose_name="Date limite de candidature")

    # ── Scraping & Postulat Externe ───────────────────────────
    source_url = models.URLField(
        blank=True, null=True, max_length=500,
        verbose_name="Lien d'origine pour postuler"
    )
    contact_email = models.EmailField(
        blank=True, null=True,
        verbose_name="Email de contact"
    )
    published_date = models.DateField(
        blank=True, null=True,
        verbose_name="Date de publication (externe)"
    )
    source_platform = models.CharField(
        max_length=50, blank=True, null=True,
        verbose_name="Plateforme source (LinkedIn, Indeed, etc.)"
    )

    # ── NLP pré-calculé (Phase 4) ─────────────────────────────
    offer_vector_json = models.TextField(blank=True, null=True,
                                         verbose_name="Vecteur TF-IDF (JSON)")

    # ── Timestamps ────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Offre de Stage"
        verbose_name_plural = "Offres de Stage"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


# ─────────────────────────────────────────────────────────────────────────────
# 2. APPLICATION — Candidature étudiant → offre
# ─────────────────────────────────────────────────────────────────────────────

class Application(models.Model):
    """
    Candidature d'un étudiant à une offre de stage.
    Contrainte UNIQUE (student, offer) : un étudiant ne peut postuler
    qu'une seule fois par offre.
    """

    class Status(models.TextChoices):
        PENDING   = 'pending',   'En attente'
        ACCEPTED  = 'accepted',  'Acceptée'
        REJECTED  = 'rejected',  'Refusée'
        WITHDRAWN = 'withdrawn', 'Retirée'

    # ── Les deux parties de la candidature ────────────────────
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Étudiant"
    )
    offer = models.ForeignKey(
        InternshipOffer,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name="Offre"
    )

    # ── Contenu ───────────────────────────────────────────────
    cover_letter = models.TextField(blank=True, null=True,
                                    verbose_name="Lettre de motivation")

    # ── Statut géré par l'entreprise ──────────────────────────
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )

    # ── Timestamps ────────────────────────────────────────────
    applied_at  = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        unique_together = ('student', 'offer')   # Contrainte DB unique
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.user.username} → {self.offer.title} [{self.status}]"
