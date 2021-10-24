from common.models import BaseManager
from django.db import models
from django.db.models.aggregates import Avg, Count, Max, Min
from django.db.models.expressions import F, Value, Window
from django.db.models.functions import Cast, DenseRank


class ChampionKillQuerySet(models.QuerySet):
    length=Count('sequence')
    avg_damage=Avg('sequence__damage')
    avg_damage_contribution=Avg('sequence__damage_contribution')
    avg_interval=(
        Cast(Max('sequence__time') - Min('sequence__time'), models.FloatField())
        / F('length')
    )

    def annotate_avg(self):
        return self.annotate(
            avg_damage=self.avg_damage,
            avg_damage_contribution=self.avg_damage_contribution,
            avg_interval=self.avg_interval,
        )

    def annotate_length(self):
        return self.annotate(
            length=self.length
        )

    def annotate_rank(self):
        min_max = self.get_avg_min_max()
        return self.annotate(
            nor_damage=self.normalize('avg_damage', min_max),
            nor_avg_damage_contribution=self.normalize('avg_damage_contribution', min_max),
            nor_interval=self.normalize('avg_interval', min_max, reverse=True),
            interested_score=(F('nor_damage') + F('nor_avg_damage_contribution') + F('nor_interval')),
            rank=Window(DenseRank(), order_by=F('interested_score').desc())
        )

    def get_avg_min_max(self):
        return self.aggregate(
            Min('avg_damage'), Max('avg_damage'),
            Min('avg_damage_contribution'), Max('avg_damage_contribution'),
            Min('avg_interval'), Max('avg_interval')
        )

    @staticmethod
    def normalize(name, min_max, reverse=False):
        min = Value(min_max[name + '__min'])
        max = Value(min_max[name + '__max'])
        normalized = (F(name) - min) / (max - min)
        return normalized if not reverse else (1 - normalized)


class ChampionKillManager(BaseManager):

    def get_queryset(self):
        return ChampionKillQuerySet(self.model, using=self._db).annotate_length()

    def interested_kills(self):
        return (self.get_queryset().filter(length__in=[3, 4, 5])
                                   .annotate_avg()
                                   .annotate_rank().order_by('rank'))
