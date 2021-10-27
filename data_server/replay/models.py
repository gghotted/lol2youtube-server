from common.models import BaseModel
from django.db import models


class ReplaySource(BaseModel):
    file = models.FileField(upload_to='replay/%Y/%m/%d')
    # upload_info = models.ForeignKey('youtube.UploadInfo', null=True, blank=True)

    class Meta:
        abstract = True


class KillReplay(ReplaySource):
    event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING)

