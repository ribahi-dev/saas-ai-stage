"""
ai/models.py - Recommendation cache model
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from offers.models import InternshipOffer
from users.models import StudentProfile


class Recommendation(models.Model):
    """
    Cache du score de correspondance entre un etudiant et une offre.
    """

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="recommendations",
        verbose_name="Etudiant",
    )
    offer = models.ForeignKey(
        InternshipOffer,
        on_delete=models.CASCADE,
        related_name="recommendations",
        verbose_name="Offre",
    )
    score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        verbose_name="Score de similarite",
    )
    insights = models.JSONField(
        blank=True,
        null=True,
        default=dict,
        verbose_name="Details de recommandation",
    )
    computed_at = models.DateTimeField(auto_now=True, verbose_name="Calcule le")

    class Meta:
        verbose_name = "Recommandation"
        verbose_name_plural = "Recommandations"
        unique_together = ("student", "offer")
        ordering = ["-score"]

    def __str__(self):
        return f"{self.student.user.username} <-> {self.offer.title} [score={self.score:.2f}]"
