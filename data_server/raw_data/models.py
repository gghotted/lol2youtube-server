from django.db import models

from common.models import BaseModel


class JsonData(BaseModel):
    TYPE_CHOICES = (
        ('summoner', 'summoner'),
        ('match', 'match'),
        ('timeline', 'timeline'),
    )
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    source_url = models.URLField()
