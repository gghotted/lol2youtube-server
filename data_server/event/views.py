from rest_framework.generics import RetrieveAPIView

from event.models import ChampionKill
from event.serializers import NotRecordedChampionKillSerializer


class NotRecordedChampionKillDetailView(RetrieveAPIView):
    serializer_class = NotRecordedChampionKillSerializer
    queryset = ChampionKill.objects.not_recorded()

    def get_object(self):
        return self.get_queryset().first()
