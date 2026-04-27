"""
offers/admin.py — Interface d'administration pour les Offres et Candidatures
"""

from django.contrib import admin
from .models import InternshipOffer, Application


@admin.register(InternshipOffer)
class InternshipOfferAdmin(admin.ModelAdmin):
    list_display  = ('title', 'company', 'status', 'location', 'duration_months',
                     'is_paid', 'deadline', 'created_at')
    list_filter   = ('status', 'is_paid', 'duration_months')
    search_fields = ('title', 'description', 'required_skills', 'company__company_name')
    readonly_fields = ('created_at', 'updated_at', 'offer_vector_json')
    ordering      = ('-created_at',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('company', 'title', 'description', 'status')
        }),
        ('Compétences & NLP', {
            'fields': ('required_skills', 'offer_vector_json'),
            'classes': ('collapse',),
        }),
        ('Logistique', {
            'fields': ('location', 'duration_months', 'is_paid', 'salary', 'deadline')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display  = ('student', 'offer', 'status', 'applied_at', 'reviewed_at')
    list_filter   = ('status',)
    search_fields = ('student__user__username', 'offer__title')
    readonly_fields = ('applied_at', 'reviewed_at')
    ordering      = ('-applied_at',)
