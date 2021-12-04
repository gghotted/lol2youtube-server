from common.models import BaseModel
from django.db import models


class Champion(BaseModel):
    eng_name = models.CharField(primary_key=True, max_length=64)
    kor_name = models.CharField(max_length=64, blank=True)
