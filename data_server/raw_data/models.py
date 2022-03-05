from datetime import datetime

from common.models import BaseManager, BaseModel
from django.db import models
from django.db.models import Max
from django.db.models.aggregates import Max
from django.db.models.expressions import F
from easydict import EasyDict


class JsonDataManager(models.Manager):
    def summoners(self):
        return self.get_queryset().filter(api_info__type='summoner')

    def matches(self):
        return (self.get_queryset()
                    .filter(api_info__type='match')
                    .annotate(game_creation=Max('matches__game_creation'))
                    .annotate(max_kill_length=Max('matches__timeline__championkills__length')))

    def timelines(self):
        return self.get_queryset().filter(api_info__type='timeline')


class APICallInfo(BaseModel):
    TYPE_CHOICES = (
        ('summoner', 'summoner'),
        ('match', 'match'),
        ('match_list', 'match_list'),
        ('timeline', 'timeline'),
    )
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    url = models.URLField()
    apikey = models.ForeignKey('raw_data.APIKey', models.DO_NOTHING, related_name='call_infos', default=1)


class JsonData(BaseModel):
    data = models.JSONField()
    api_info = models.OneToOneField(APICallInfo, models.CASCADE, null=True)
    parse_success = models.BooleanField(default=False)
    objects = JsonDataManager()

    @property
    def dot_data(self):
        return EasyDict(self.data)


class APIKeyManager(BaseManager):
    def get_usable_key(self):
        return (self.filter(lock_until__lt=datetime.now())
                    .annotate(last_used=Max('call_infos__created'))
                    .order_by('last_used')
                    .first()
                )

    def get_wait_secs(self):
        fastest_apikey = self.order_by('lock_until').first()
        return (fastest_apikey.lock_until - datetime.now()).seconds


class APIKey(BaseModel):
    lock_until = models.DateTimeField(default=datetime.min)
    key = models.CharField(max_length=128, blank=True)
    objects = APIKeyManager()


class CrawlableMatch(BaseModel):
    id = models.CharField(primary_key=True, max_length=64)
    used = models.BooleanField(default=False)

    def crawl(self):
        pass
