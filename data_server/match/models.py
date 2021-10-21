from datetime import datetime

from common.models import BaseManager, BaseModel
from django.db import models
from django.db.models import F
from raw_data.riot_api import MatchAPI
from summoner.models import Summoner


class MatchManager(BaseManager):

    def creates_from_api(self, match_list):
        for match_id in match_list:
            self.create_from_api(match_id=match_id)

    def get_queryset(self):
        return super().get_queryset().annotate(
            is_interested=(
                F('has_pentakill')
                .bitor(F('has_quadrakill'))
                .bitor(F('has_triplekill'))
            )
        )


class Match(BaseModel):
    json = models.ForeignKey('raw_data.JsonData', models.DO_NOTHING)
    id = models.CharField(primary_key=True, max_length=64)
    game_creation = models.DateTimeField()
    has_pentakill = models.BooleanField()
    has_quadrakill = models.BooleanField()
    has_triplekill = models.BooleanField()
    queue_id = models.PositiveIntegerField()

    objects = MatchManager()
    api_call_class = MatchAPI

    @staticmethod
    def parse_id(data):
        return data.metadata.matchId

    @staticmethod
    def parse_game_creation(data):
        return datetime.fromtimestamp(
            data.info.gameCreation / 1000
        )

    @staticmethod
    def parse_has_pentakill(data):
        pentakills = sum(
            participant.pentaKills
            for participant in data.info.participants
        )
        return pentakills > 0

    @staticmethod
    def parse_has_quadrakill(data):
        quadrakills = sum(
            participant.quadraKills
            for participant in data.info.participants
        )
        return quadrakills > 0

    @staticmethod
    def parse_has_triplekill(data):
        triplekills = sum(
            participant.tripleKills
            for participant in data.info.participants
        )
        return triplekills > 0

    @staticmethod
    def parse_queue_id(data):
        return data.info.queueId

    @property
    def summoners(self):
        return Summoner.objects.filter(participants__match=self)


class Participant(BaseModel):
    match = models.ForeignKey(Match, models.CASCADE, related_name='participants')
    summoner = models.ForeignKey('summoner.Summoner', models.DO_NOTHING, related_name='participants')
    index = models.PositiveIntegerField()
    champion = models.CharField(max_length=64)

    @staticmethod
    def parse_summoner(data):
        return Summoner.objects.get_or_create(puuid=data.puuid, defaults={'name': data.summonerName})[0]

    @staticmethod
    def parse_champion(data):
        return data.championName

    @staticmethod
    def parse_index(data):
        return data.participantId
