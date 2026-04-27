"""
offers/serializers.py — Sérialisation des Offres et Candidatures
"""

from rest_framework import serializers
from django.utils import timezone

from .models import InternshipOffer, Application
from users.serializers import CompanyProfileSerializer, StudentProfileSerializer


# ─────────────────────────────────────────────────────────────────────────────
# 1. INTERNSHIP OFFER SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────

class InternshipOfferSerializer(serializers.ModelSerializer):
    """
    Sérialise une offre de stage.
    - En lecture  : inclut les infos entreprise (nested)
    - En écriture : company est déduit automatiquement de l'utilisateur connecté
    """
    company_info  = CompanyProfileSerializer(source='company', read_only=True)
    is_active     = serializers.BooleanField(read_only=True)
    applications_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = InternshipOffer
        fields = (
            'id', 'company', 'company_info',
            'title', 'offer_type', 'description', 'required_skills',
            'location', 'duration_months', 'is_paid', 'salary',
            'status', 'is_active', 'deadline',
            'source_url', 'contact_email', 'published_date', 'source_platform',
            'applications_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'company', 'company_info', 'created_at', 'updated_at')

    def get_applications_count(self, obj):
        return obj.applications.count()

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "La date limite ne peut pas être dans le passé."
            )
        return value

    def validate(self, attrs):
        if attrs.get('is_paid') and not attrs.get('salary'):
            raise serializers.ValidationError(
                {"salary": "Veuillez indiquer le montant si le stage est rémunéré."}
            )
        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# 2. APPLICATION SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────

class ApplicationSerializer(serializers.ModelSerializer):
    """
    Sérialise une candidature.
    - En lecture  : inclut les infos étudiant et offre
    - En écriture : student et offer sont déduits du contexte
    """
    student_info = StudentProfileSerializer(source='student', read_only=True)
    offer_info   = InternshipOfferSerializer(source='offer', read_only=True)

    class Meta:
        model  = Application
        fields = (
            'id', 'student', 'student_info',
            'offer', 'offer_info',
            'cover_letter', 'status',
            'applied_at', 'reviewed_at',
        )
        read_only_fields = ('id', 'student', 'student_info', 'offer_info',
                            'status', 'applied_at', 'reviewed_at')

    def validate(self, attrs):
        student = self.context['request'].user.student_profile
        offer   = attrs.get('offer')
        if offer and Application.objects.filter(student=student, offer=offer).exists():
            raise serializers.ValidationError(
                "Vous avez déjà postulé à cette offre."
            )
        if offer and not offer.is_active:
            raise serializers.ValidationError(
                "Cette offre n'est plus active."
            )
        return attrs


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """
    Utilisé par l'entreprise pour changer le statut d'une candidature.
    Seul le champ `status` est modifiable.
    """
    class Meta:
        model  = Application
        fields = ('id', 'status', 'reviewed_at')
        read_only_fields = ('id', 'reviewed_at')

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.reviewed_at = timezone.now()
        instance.save()
        return instance
