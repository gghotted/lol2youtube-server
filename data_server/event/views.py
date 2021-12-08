from rest_framework.generics import RetrieveAPIView

from event.models import ChampionKill
from event.serializers import NotRecordedChampionKillSerializer


class NotRecordedChampionKillDetailView(RetrieveAPIView):
    serializer_class = NotRecordedChampionKillSerializer
    queryset = ChampionKill.objects.not_recorded_pentakills()

    def get_object(self):
        killer = self.request.GET.get('killer')
        qs = self.get_queryset()
        if killer:
            qs = qs.filter(killer__champion__eng_name=killer)
        return qs.first()

    def get_serializer(self, kill_event, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(kill_event.sequence.all(), **kwargs, many=True)
