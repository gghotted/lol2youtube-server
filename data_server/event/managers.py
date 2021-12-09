from common.models import BaseManager
from django.db import models
from match.models import Version
from replay.models import KillReplay, ReplayBlackList


class InterestScoreManager(BaseManager):
    def create_normalized_scores(self, min_boundary=float('-inf'), max_boundary=float('inf'), low_is_good=False):
        if self.model.objects.exists():
            raise Exception('이미 스코어 객체가 존재합니다')

        target_model = self.model.target_model
        target_field = self.model.target_field
        values = (
            target_model.objects
            .order_by(target_field)
            .values_list(target_field, flat=True)
        )
        indexes = range(0, len(values), round(len(values) / 9))
        boundary_values = [min_boundary] + [values[i] for i in indexes] + [max_boundary]

        scores = range(1, 11)
        if low_is_good:
            scores = reversed(scores)

        for i, score in enumerate(scores):
            self.create(
                min_boundary=boundary_values[i],
                max_boundary=boundary_values[i + 1],
                value=score
            )


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
        return (qs
            .exclude(timeline__id__in=blacklist_match_ids)
            .filter(timeline__match__version__useable=True)
        )

    def not_recorded_pentakills(self):
        return self.get_queryset().pentakills().not_recorded()
