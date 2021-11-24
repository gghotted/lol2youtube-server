from django.conf import settings
from django.db.models.aggregates import Max
from django.db.models.query import QuerySet
from event.models import ChampionKill
from raw_data.models import JsonData

from data_cleaner.base import DataCleaner, DeleteQueryset, ExcludeQueryset


class Pentakill(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = ChampionKill.objects.filter(length=5).values('timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class Recorded(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = ChampionKill.objects.all().recorded().values('timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class NotInterestedKill(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = ChampionKill.objects.exclude(length=5).values('timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class JsonDataCleaner(DataCleaner):
    start_queryset = JsonData.objects.matches()
    delete_queryset_list = [NotInterestedKill()]
    exclude_queryset_list = [Pentakill(), Recorded()]
    model = JsonData
    remain_delete_count = settings.JSON_DATA_REMAIN_COUNT
    ordering = ['-game_creation']
