"""
ai/admin.py — Interface d'administration pour les Recommandations
"""

from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display  = ('student', 'offer', 'score_display', 'computed_at')
    list_filter   = ()
    search_fields = ('student__user__username', 'offer__title')
    readonly_fields = ('score', 'computed_at')
    ordering      = ('-score',)

    def score_display(self, obj):
        percent = round(obj.score * 100, 1)
        return f"{percent}%"
    score_display.short_description = "Score"
    score_display.admin_order_field = 'score'
