from itertools import islice

import numpy as np
from common.models import BaseManager
from django.apps import apps
from django.db import models
from django.db.models import F, Sum
from match.models import Version
from replay.models import KillReplay, ReplayBlackList


class InterestScoreManager(BaseManager):
    '''
    *** 이 객체를 사용할 때는 signal을 비활성화 하시오 ***
    '''

    def update_or_create_normalized_scores(self):      
        boundary_values = self._get_boundary_values()
        pk_list = []
        for i, score in enumerate(self._get_scores()):
            obj = self.update_or_create(
                value=score,
                defaults={
                    'lte_boundary': boundary_values[i],
                    'gt_boundary': boundary_values[i + 1],
                }
            )[0]
            pk_list.append(obj.pk)

        return self.filter(pk__in=pk_list)

    def sync_normalized_scores(self):
        score_qs = self.update_or_create_normalized_scores()
        target_model = apps.get_model(*self.model.target_model.split('.'))
        target_field = self.model.target_field
        score_field = target_field + self.model.score_field_postfix

        for score_obj in score_qs:
            '''
            lte_boundary   gt_boundary
            *              o

            lte_boundary보다 크거나 같고
            gt_boundary보다 작은 것을 필터링
            '''
            filter_dict = {
                target_field + '__gte': score_obj.lte_boundary,
                target_field + '__lt': score_obj.gt_boundary,
            }
            target_model.base_manager.filter(**filter_dict).update(**{
                score_field: score_obj,
            })


    def _get_scores(self):
        scores = range(1, 11)
        if self.model.low_is_good:
            scores = reversed(scores)
        return scores

    def _get_boundary_values(self):
        target_model = apps.get_model(*self.model.target_model.split('.'))
        target_field = self.model.target_field
        values = (
            target_model.base_manager
            .filter(**self.model.normalize_qs_filters)
            .order_by(target_field)
            .values_list(target_field, flat=True)
        )
        boundary_values = []
        for group in np.array_split(values, 9):
            idx = int(len(group) / 2)
            boundary_values.append(
                group[idx]
            )
        return [float('-inf')] + boundary_values + [float('inf')]


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
            .order_by('duration')
        )

    def not_recorded_pentakills(self):
        return self.get_queryset().pentakills().not_recorded()
