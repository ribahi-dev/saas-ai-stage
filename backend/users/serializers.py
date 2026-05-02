"""
users/serializers.py — Sérialisation des données utilisateur

Un serializer DRF joue deux rôles :
  1. VALIDATION  : vérifie les données entrantes (register, update profil)
  2. SÉRIALISATION : transforme un objet Python en JSON pour la réponse

Architecture :
  - UserSerializer          → Représentation générale d'un User
  - RegisterSerializer      → Inscription (création de compte)
  - StudentProfileSerializer → Profil complet d'un étudiant
  - CompanyProfileSerializer → Profil complet d'une entreprise
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import StudentProfile, CompanyProfile

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# 1. USER SERIALIZER — Représentation publique d'un compte
# ─────────────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    Utilisé pour retourner les infos de l'utilisateur connecté (GET /me/).
    NE retourne JAMAIS le mot de passe.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'role')


# ─────────────────────────────────────────────────────────────────────────────
# 2. REGISTER SERIALIZER — Création de compte
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Gère l'inscription d'un nouvel utilisateur.
    - `password` : write_only → n'est jamais renvoyé dans la réponse
    - `password2` : confirmation, seulement pour la validation
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirmez le mot de passe"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'role', 'password', 'password2')

    def validate(self, attrs):
        """Vérifie que les deux mots de passe correspondent."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )
        # Email normalise (trim + minuscules) : un seul compte par boite mail
        raw_email = attrs.get('email') or ''
        email = raw_email.strip().lower()
        attrs['email'] = email
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                {
                    "email": (
                        "Cet email est deja lie a un compte. Connectez-vous "
                        "ou utilisez une autre adresse."
                    ),
                }
            )
        return attrs

    def create(self, validated_data):
        """
        Crée le User + son profil associé (Student ou Company) en une transaction.
        On utilise create_user() qui hash automatiquement le mot de passe.
        """
        validated_data.pop('password2')
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.STUDENT)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Création automatique du profil associé au rôle
        if role == User.Role.STUDENT:
            StudentProfile.objects.create(user=user)
        elif role == User.Role.COMPANY:
            CompanyProfile.objects.create(user=user, company_name=user.username)

        return user


# ─────────────────────────────────────────────────────────────────────────────
# 3. STUDENT PROFILE SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────

class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Profil étudiant complet — inclut les infos du compte parent via UserSerializer.
    Utilisé pour GET et PATCH sur /api/users/me/student-profile/
    """
    user = UserSerializer(read_only=True)
    target_job_titles = serializers.ListField(child=serializers.CharField(), required=False)
    preferred_locations = serializers.ListField(child=serializers.CharField(), required=False)
    preferred_offer_types = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'user',
            'bio', 'phone', 'linkedin_url',
            'university', 'field_of_study', 'graduation_year',
            'cv_file',
            'extracted_skills', 'experience_level', 'projects',
            'target_job_titles', 'preferred_locations', 'preferred_offer_types',
            'remote_ok', 'expected_salary',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'user', 'cv_file',
            'extracted_skills', 'experience_level', 'projects',
            'created_at', 'updated_at',
        )

    def validate_preferred_offer_types(self, value):
        allowed = {'stage', 'emploi', 'freelance'}
        invalid = [item for item in value if item not in allowed]
        if invalid:
            raise serializers.ValidationError("Types d'offres invalides.")
        return value


# ─────────────────────────────────────────────────────────────────────────────
# 4. COMPANY PROFILE SERIALIZER
# ─────────────────────────────────────────────────────────────────────────────

class CompanyProfileSerializer(serializers.ModelSerializer):
    """
    Profil entreprise complet.
    Utilisé pour GET et PATCH sur /api/users/me/company-profile/
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = CompanyProfile
        fields = (
            'id', 'user',
            'company_name', 'description', 'website',
            'industry', 'city', 'country', 'logo',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
