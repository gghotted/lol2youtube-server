from common.models import BaseModel
from django.db import models


class ReplayBlackList(BaseModel):
    match = models.ForeignKey('match.Match', on_delete=models.CASCADE)
    msg = models.TextField(blank=True)


class ReplaySource(BaseModel):
    UPLOAD_STATUS_CHOICES = [
        ('분류 대기중', '분류 대기중'),
        ('업로드 대기중', '업로드 대기중'),
        ('업로드됨', '업로드됨'),
        ('삭제 대기중', '삭제 대기중'),
    ]
    file = models.FileField(upload_to='replay/%Y/%m/%d')
    upload_status = models.CharField(max_length=32, choices=UPLOAD_STATUS_CHOICES, default=UPLOAD_STATUS_CHOICES[0][0])
    # upload_info = models.ForeignKey('youtube.UploadInfo', null=True, blank=True)

    class Meta:
        abstract = True


class KillReplay(ReplaySource):
    event = models.ForeignKey('event.ChampionKill', on_delete=models.DO_NOTHING, related_name='replays')
