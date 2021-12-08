from django.conf import settings
from django.db.models.aggregates import Max
from django.db.models.query import QuerySet
from event.models import ChampionKill
from match.models import Match
from raw_data.models import JsonData
from replay.models import KillReplay

from data_cleaner.base import DataCleaner, DeleteQueryset, ExcludeQueryset


class Pentakill(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = (
            ChampionKill.base_manager
            .filter(length=5)
            .filter(timeline__match__version__useable=True)
            .values('timeline__match__json__id')
        )
        return qs.filter(id__in=json_ids)


class Recorded(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = KillReplay.base_manager.values('event__timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class NotInterestedKill(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = ChampionKill.base_manager.exclude(length=5).values('timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class NotUseableMatch(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = Match.base_manager.filter(version__useable=False).values('json__id')
        return qs.filter(id__in=json_ids)


class JsonDataCleaner(DataCleaner):
    start_queryset = JsonData.objects.matches()
    delete_queryset_list = [NotInterestedKill(), NotUseableMatch()]
    exclude_queryset_list = [Pentakill(), Recorded()]
    model = JsonData
    remain_delete_count = settings.JSON_DATA_REMAIN_COUNT
    ordering = ['-game_creation']
