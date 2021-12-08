from common.models import BaseManager
from django.db import models
from replay.models import KillReplay, ReplayBlackList


class ChampionKillQuerySet(models.QuerySet):
    def not_recorded(self):
        recorded_ids = KillReplay.objects.values('event__id')
        return self.exclude(id__in=recorded_ids)

    def recorded(self):
        recorded_ids = KillReplay.objects.values('event__id')
        return self.filter(id__in=recorded_ids)

    def pentakills(self):
        return self.filter(length=5, timeline__match__has_pentakill=True)


class ChampionKillManager(BaseManager):

    def get_queryset(self):
        qs = ChampionKillQuerySet(self.model, using=self._db)
        blacklist_match_ids = ReplayBlackList.objects.values('match__id')
        return qs.exclude(timeline__id__in=blacklist_match_ids)

    def not_recorded_pentakills(self):
        return self.get_queryset().pentakills().not_recorded()
