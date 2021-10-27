from common.models import BaseModel
from django.db import models


class Replay(BaseModel):
    uploaded_at = models.DateTimeField()
    is_uploaded = models.BooleanField(default=False)
    file = models.FileField(upload_to='replay/%Y/%m/%d')
    title = models.CharField(max_length=255)
    description = models.TextField()
    yt_link = models.URLField()
    # tags = models.ForeignKey('youtube.Tag', on_delete=models.DO_NOTHING)
    # yt_account = models.ForeignKey('youtube.Account', on_delete=models.DO_NOTHING)


class KillReplay(Replay):
    kill_event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING)

