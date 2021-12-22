from django.conf import settings
from django.db.models.aggregates import Count, Max
from django.db.models.query import QuerySet
from event.models import ChampionKill
from match.models import Match
from raw_data.models import JsonData
from replay.models import KillReplay
from timeline.models import Timeline
from youtube.models import UploadInfo

from data_cleaner.base import DataCleaner, DeleteQueryset, ExcludeQueryset


class Pentakill(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = (
            ChampionKill.objects
            .all()
            .not_recorded()
            .filter(length=5)
            .filter(timeline__match__version__useable=True)
            .values('timeline__match__json__id')
        )
        return qs.filter(id__in=json_ids)


class BestUltimateHitCount(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = (
            ChampionKill.objects
            .all()
            .not_recorded()
            .filter(length__in=[3, 4, 5])
            .filter(timeline__match__version__useable=True)
            .order_by('-sequence_ultimate_hit_count')
            .values('timeline__match__json__id')[:50]
        )
        return qs.filter(id__in=json_ids)


class NotUploaded(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = KillReplay.base_manager.filter(file__upload_info=None).values('event__timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class Recorded(ExcludeQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = KillReplay.base_manager.values('event__timeline__match__json__id')
        return qs.filter(id__in=json_ids)

    
class Uploaded(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = UploadInfo.base_manager.values('file__replay__event__timeline__match__json__id')
        return qs.filter(id__in=json_ids)


class NoEvent(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = Timeline.base_manager.annotate(c=Count('events')).filter(c=0).values('match__json__id')
        return qs.filter(id__in=json_ids)


class NoPentakill(DeleteQueryset):
    def get_queryset(self, qs: QuerySet):
        json_ids = Match.base_manager.filter(has_pentakill=False).values('json__id')
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
    delete_queryset_list = [NotInterestedKill(), NotUseableMatch(), NoPentakill()]
    exclude_queryset_list = [Pentakill(), BestUltimateHitCount(), NotUploaded()]
    model = JsonData
    remain_delete_count = settings.JSON_DATA_REMAIN_COUNT
    ordering = ['-game_creation']
