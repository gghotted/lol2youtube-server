from common.models import BaseModel
from django.conf import settings
from django.db import models
from django.db.models.aggregates import Count

from youtube.managers import UploadInfoManager
from youtube.uploader import get_authenticated_service, get_upload_request


class ChannelGroup(BaseModel):
    name = models.CharField(primary_key=True, max_length=128)
    description = models.TextField()

    def get_channel_to_upload(self):
        return self.channels.annotate(upload_count=Count('upload_infos')).order_by('upload_count').first()


class Channel(BaseModel):
    name = models.CharField(primary_key=True, max_length=128)
    group = models.ForeignKey('youtube.ChannelGroup', models.DO_NOTHING, related_name='channels')
    description = models.TextField()
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)


class UploadInfo(BaseModel):
    URL_PREFIX = 'https://www.youtube.com/watch?v='
    GAMING_CATEGORY = 20
    PRIVACY_STATUSES = (
        ('public', 'public'),
        ('private', 'private'),
        ('unlisted', 'unlisted'),
    )
    channel_group = models.ForeignKey('youtube.ChannelGroup', models.DO_NOTHING, related_name='upload_infos')
    channel = models.ForeignKey('youtube.Channel', models.DO_NOTHING, related_name='upload_infos', null=True)
    file = models.OneToOneField('replay.ReplayFile', models.DO_NOTHING, related_name='upload_info')
    title = models.CharField(max_length=256)
    description = models.TextField()
    category_id = models.CharField(max_length=8, default=GAMING_CATEGORY)
    privacy_status = models.CharField(max_length=16, choices=PRIVACY_STATUSES, default='public')
    embeddable = models.BooleanField(default=True)
    url = models.URLField(blank=True)
    objects = UploadInfoManager()


    def upload(self):
        self.channel = self.channel_group.get_channel_to_upload()
        youtube = get_authenticated_service(
            self.channel.access_token,
            self.channel.refresh_token,
            settings.YOUTUBE_CLIENT_ID,
            settings.YOUTUBE_CLIENT_SECRET,
        )
        upload_request = get_upload_request(
            youtube,
            self.file.file.path, # need temporary file?
            self.title,
            self.description,
            self.category_id,
            self.privacy_status,
            self.embeddable
        )
        res = upload_request.execute()
        self.url = self.URL_PREFIX + res['id']

        if self.channel.access_token != upload_request.http.credentials.token:
            self.channel.access_token = upload_request.http.credentials.token
            self.channel.save()
        self.save()
        self.file.delete_file()
