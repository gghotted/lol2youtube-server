from common.models import BaseManager, BaseModel
from django.db import models
from django.db.models import Count, Q


class ChampionManager(BaseManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            match_count=Count('participants'),
            kill_count=Count('participants__kill_events'),
            pentakill_count=Count('participants', filter=Q(participants__kill_events__length=5)),
        )


class Champion(BaseModel):
    eng_name = models.CharField(primary_key=True, max_length=64)
    kor_name = models.CharField(max_length=64, blank=True)
    objects = ChampionManager()


class Ultimate(BaseModel):
    INTEREST_ULTIMATE_CHAMPION_NAME = {
        'Rakan',
        'Poppy',
        'Braum',
        'Orianna',
        'Kennen',
        'Velkoz',
        'Aphelios',
        'Bard',
        'Qiyana',
        'Rumble',
        'Jinx',
        'Seraphine',
        'Riven',
        'Nunu',
        'Malphite',
        'Morgana',
        'Leona',
        'Neeko',
        'Illaoi',
        'Sion',
        'Volibear',
        'Cassiopeia',
        'Hecarim',
        'Galio',
        'Nautilus',
        'Sona',
        'Azir',
        'Irelia',
        'Ekko',
        'Yone',
        'Sett',
        'Fizz',
        'Rell',
        'Gragas',
        'Evelynn',
        'Rammus',
        'Yasuo',
        'Diana',
        'Lissandra',
        'LeeSin',
        'Pantheon',
        'Gnar',
        'Annie',
        'Vladimir',
        'Talon',
        'Amumu',
        'JarvanIV',
        'MonkeyKing',
    }
    champion = models.OneToOneField('champion.Champion', models.CASCADE, related_name='ultimate')
