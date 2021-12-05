from common.models import BaseModel
from django.db import models


class ReplayBlackList(BaseModel):
    match = models.ForeignKey('match.Match', on_delete=models.CASCADE)
    msg = models.TextField(blank=True)


class ReplaySource(BaseModel):

    class Meta:
        abstract = True


class KillReplay(ReplaySource):
    event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING, related_name='killreplay')