import requests
from common.models import BaseModel
from django.conf import settings
from django.db import models
from django.db.models.aggregates import Count


class UploadInfo(BaseModel):
    URL_PREFIX = 'https://www.youtube.com/watch?v='
    GAMING_CATEGORY = 20
    PRIVACY_STATUSES = (
        ('public', 'public'),
        ('private', 'private'),
        ('unlisted', 'unlisted'),
    )
    file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='upload_info')
    title = models.CharField(max_length=256)
    description = models.TextField()
    category_id = models.CharField(max_length=8, default=GAMING_CATEGORY)
    privacy_status = models.CharField(max_length=16, choices=PRIVACY_STATUSES, default='public')
    embeddable = models.BooleanField(default=True)
    url = models.URLField(blank=True)
    channel_name = models.CharField(max_length=64, blank=True, default='')
    is_backuped = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )

    def post_backup_data(self):
        url = settings.BACKUP_HOST + '/replay/pentakills'
        event = self.file.replay.event
        match = event.timeline.match
        champion = event.killer.champion
        res = requests.post(
            url,
            data={
                'url': self.url,
                'match_id': match.id,
                'game_creation': match.game_creation,
                'game_version': match.version.str,
                'upload_channel': self.channel_name,
                'kill_duration': round(event.duration * event.length),
                'damage_contribution': event.damage_contribution,
                'ultimate_hit_count': event.sequence_ultimate_hit_count,
                'champion.eng_name': champion.eng_name,
                'champion.kor_name': champion.kor_name,
            },
            verify=False,
        )
        if res.status_code == 201:
            self.is_backuped = True
            self.save()


class CommentAD(BaseModel):
    upload_info = models.OneToOneField('youtube.UploadInfo', models.CASCADE, related_name='comment_ad')
    content = models.TextField()
