"""
users/admin.py — Interface d'administration pour les utilisateurs et profils
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, StudentProfile, CompanyProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Étend l'admin Django standard pour afficher le champ `role`.
    """
    list_display  = ('username', 'email', 'first_name', 'last_name', 'role',
                     'is_staff', 'is_active', 'date_joined')
    list_filter   = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering      = ('-date_joined',)

    # Ajout du champ `role` dans le formulaire de modification
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Rôle Plateforme', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Rôle Plateforme', {'fields': ('role',)}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'university', 'field_of_study',
                     'graduation_year', 'has_cv', 'updated_at')
    search_fields = ('user__username', 'university', 'field_of_study')
    readonly_fields = ('cv_text_extracted', 'cv_vector_json', 'created_at', 'updated_at')
    ordering      = ('-updated_at',)

    def has_cv(self, obj):
        return bool(obj.cv_file)
    has_cv.boolean = True
    has_cv.short_description = "CV ?"


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display  = ('company_name', 'user', 'industry', 'city', 'country', 'updated_at')
    search_fields = ('company_name', 'user__username', 'industry', 'city')
    readonly_fields = ('created_at', 'updated_at')
    ordering      = ('company_name',)
