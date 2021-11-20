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
        'id',
        'length',
        'created',
        'replay',
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

    def get_queryset(self, request):
        replays = KillReplay.objects.filter(event=OuterRef('pk'))
        return ChampionKill.objects.interested_kills().annotate(
            replay_url=Subquery(replays.values('file')[:1], output_field=models.CharField())
        )

    def get_ordering(self, request):
        return ('replay_url', '-created')

    @admin.display(ordering='rank')
    def rank(self, obj):
        return obj.rank

    @admin.display(ordering='interested_score')
    def interested_score(self, obj):
        return obj.interested_score

    @admin.display(ordering='length')
    def length(self, obj):
        return obj.length

    @admin.display(ordering='nor_avg_damage_contribution')
    def nor_avg_damage_contribution(self, obj):
        return obj.nor_avg_damage_contribution

    @admin.display(ordering='nor_interval')
    def nor_interval(self, obj):
        return obj.nor_interval

    @admin.display(ordering='replay_url')
    def replay(self, obj):
        if not obj.replay_url:
            return None
        link = settings.MEDIA_URL + '/' + obj.replay_url
        return mark_safe('<a href="%s">link</a>' % (link))
