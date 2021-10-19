from common.models import BaseModel
from django.db import models
from easydict import EasyDict


class JsonDataManager(models.Manager):
    def summoners(self):
        return self.get_queryset().filter(api_info__type='summoner')

    def matches(self):
        return self.get_queryset().filter(api_info__type='match')

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


class JsonData(BaseModel):
    data = models.JSONField()
    api_info = models.OneToOneField(APICallInfo, models.CASCADE, null=True)
    objects = JsonDataManager()

    @property
    def dot_data(self):
        return EasyDict(self.data)
