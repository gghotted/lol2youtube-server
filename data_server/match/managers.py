from common.models import BaseManager
from django.db.models.aggregates import Count, Max


class VersionManger(BaseManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            last_game_creation=Max('matches__game_creation'),
            match_count=Count('matches'),
        )
