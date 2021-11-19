from django.contrib import admin
from django.utils.safestring import mark_safe

from event.models import ChampionKill


@admin.register(ChampionKill)
class ChampionKillAdmin(admin.ModelAdmin):
    list_display = (
        'rank',
        'interested_score',
        'length',
        'nor_avg_damage_contribution',
        'nor_interval',
        'replay',
    )

    def get_queryset(self, request):
        return ChampionKill.objects.interested_kills()

    def get_ordering(self, request):
        return ('rank', )

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

    @admin.display(ordering='replays__file')
    def replay(self, obj):
        replay = obj.replays.first()

        if not replay:
            return None

        return mark_safe('<a href="%s">link</a>' % (replay.file.url))

