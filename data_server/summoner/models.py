from datetime import datetime

from common.models import BaseManager, BaseModel
from django.conf import settings
from django.db import models
from django.db.models import Max
from raw_data.riot_api import MatchListAPI, SummonerAPI


class SummonerManager(BaseManager):
    def get_to_update(self):
        return self.order_by_update_priority().first()

    def order_by_update_priority(self):
        '''
        업데이트 최소시간을 만족하는 소환사 중
        최근 게임 순 (-recent_match_at),
        업데이트 시간이 오래된 순 (match_updated_at)
        '''
        boundary_time = datetime.now() - settings.SUMMONER_MIN_UPDATE_TIME
        return self.filter(match_updated_at__lte=boundary_time) \
                   .annotate(recent_match_at=Max('participants__match__game_creation')) \
                   .order_by('-recent_match_at', 'match_updated_at')


class Summoner(BaseModel):
    '''
    이 서비스의 핵심은 match data 이므로, puuid만 저장하고 따로 api는 요청하지 않음.
    '''
    json = models.ForeignKey('raw_data.JsonData', models.DO_NOTHING, null=True, blank=True)
    puuid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64, blank=True)
    match_updated_at = models.DateTimeField(default=datetime.min)

    objects = SummonerManager()
    api_call_class = SummonerAPI

    @staticmethod
    def parse_puuid(data):
        return data.puuid

    @staticmethod
    def parse_name(data):
        return data.name

    def update_matches(self):
        from match.models import Match

        match_list = MatchListAPI(self.puuid)().json
        Match.objects.creates_or_get_from_api(match_id=match_list)

        updated_self = Summoner.objects.get(puuid=self.puuid)
        updated_self.match_updated_at = datetime.now()
        updated_self.save()

    @property
    def matches(self):
        from match.models import Match
        return Match.objects.filter(participants__summoner=self)

