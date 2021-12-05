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
