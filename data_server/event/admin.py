from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models.expressions import OuterRef, Subquery
from django.utils.safestring import mark_safe
from replay.models import KillReplay

from event.models import ChampionKill


@admin.register(ChampionKill)
class ChampionKillAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'length',
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
    ordering = (
        '-created',
    )
    list_filter = (
        'length',
    )
