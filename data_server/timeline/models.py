from common.models import BaseModel
from django.db import models
from raw_data.riot_api import TimelineAPI


class Timeline(BaseModel):
    json = models.ForeignKey('raw_data.JsonData', models.DO_NOTHING)
    id = models.CharField(primary_key=True, max_length=64)
    match = models.OneToOneField('match.Match', models.CASCADE, related_name='timeline')

    api_call_class = TimelineAPI

    @staticmethod
    def parse_id(data):
        return data.metadata.matchId

    @staticmethod
    def parse_match_id(data):
        return data.metadata.matchId
