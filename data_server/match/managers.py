from common.models import BaseManager
from django.db.models import Q
from django.db.models.aggregates import Count, Max, Min


class VersionManger(BaseManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            first_game_creation=Min('matches__game_creation'),
            last_game_creation=Max('matches__game_creation'),
            match_count=Count('matches'),
        )

    def latest_version(self):
        return self.filter(useable=True).order_by('-last_game_creation').first()
