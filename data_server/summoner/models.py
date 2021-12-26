from datetime import datetime

from common.models import BaseManager, BaseModel
from django.conf import settings
from django.db import models
from django.db.models import Max
from django.db.models.expressions import F
from raw_data.models import JsonData
from raw_data.riot_api import ChallengerLeaguesAPI, MatchListAPI, SummonerAPI


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
        return self.filter(match_updated_at__lte=boundary_time, tier__ordering=TierOrdering.CHALLENGER) \
                   .annotate(recent_match_at=Max('participants__match__game_creation')) \
                   .order_by(F('recent_match_at').desc(nulls_last=True), 'match_updated_at')


class Summoner(BaseModel):
    '''
    이 서비스의 핵심은 match data 이므로, puuid만 저장하고 따로 api는 요청하지 않음.
    '''
    json = models.ForeignKey('raw_data.JsonData', models.CASCADE, null=True, blank=True)
    puuid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=64, blank=True)
    match_updated_at = models.DateTimeField(default=datetime.min)
    tier = models.ForeignKey('summoner.Tier', models.DO_NOTHING, null=True, related_name='summoners')

    objects = SummonerManager()
    api_call_class = SummonerAPI

    @staticmethod
    def parse_puuid(data):
        return data.puuid

    @staticmethod
    def parse_name(data):
        return data.name

    @staticmethod
    def update_challengers():
        Summoner.objects.update(tier=None)

        entries = ChallengerLeaguesAPI()().json['entries']
        pk_list = []
        for challenger in entries:
            summoner_id = challenger['summonerId']
            pk = Summoner.objects.create_or_get_from_api(summoner_id=summoner_id).pk
            pk_list.append(pk)

        challenger_obj = Tier.objects.get(ordering=TierOrdering.CHALLENGER)
        Summoner.objects.filter(pk__in=pk_list).update(tier=challenger_obj)

    def update_matches(self):
        from match.models import Match

        match_list = MatchListAPI(self.puuid)().json
        matches = Match.objects.creates_or_get_from_api(match_id=match_list)

        created_jsons = matches.values('json').union(
            matches.values('timeline__json'),
            matches.values('participants__summoner__json'),
        )
        JsonData.objects.filter(id__in=created_jsons).update(parse_success=True)

        updated_self = Summoner.objects.get(puuid=self.puuid)
        updated_self.match_updated_at = datetime.now()
        updated_self.save()

    @property
    def matches(self):
        from match.models import Match
        return Match.objects.filter(participants__summoner=self)


class TierOrdering:
    UNDEFINED = 0
    CHALLENGER = 1


class Tier(BaseModel):
    ordering = models.IntegerField()
    name = models.CharField(max_length=32)

