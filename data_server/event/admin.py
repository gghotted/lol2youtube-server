from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models import F
from django.db.models.expressions import OuterRef, Subquery
from django.utils.safestring import mark_safe
from replay.models import KillReplay

from event.models import ChampionKill, DurationScore


class InterestScoreAdmin(admin.ModelAdmin):
    list_display = (
        'value',
        'lte_boundary',
        'gt_boundary',
    )
    ordering = (
        '-value',
    )
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DurationScore)
class DurationScoreAdmin(InterestScoreAdmin):
    pass


@admin.register(ChampionKill)
class ChampionKillAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'length',
        'duration',
    )
    fields = (
        'killer',
        'victim',
    )
    readonly_fields = (
        'killer',
        'victim',
    )
    list_per_page = 20
    show_full_result_count = False
    list_filter = (
        'length',
    )

    def get_ordering(self, request):
        return (
            'duration',
            '-created',
        )

    @admin.display(ordering='duration_score__value')
    def duration_score_value(self, obj):
        try:
            return obj.duration_score.value
        except:
            return None

    @admin.display(ordering=F('interest_score').desc(nulls_last=True))
    def interest_score(self, obj):
        return obj.interest_score
