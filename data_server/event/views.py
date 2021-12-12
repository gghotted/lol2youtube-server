from rest_framework.generics import RetrieveAPIView

from event.models import ChampionKill
from event.serializers import NotRecordedChampionKillSerializer


class NotRecordedChampionKillDetailView(RetrieveAPIView):
    serializer_class = NotRecordedChampionKillSerializer
    queryset = ChampionKill.objects.not_recorded_pentakills()

    def get_object(self):
        o = self.request.GET.get('o', '-duration')
        qs = self.get_queryset().order_by(o)
        return qs.first()

    def get_serializer(self, kill_event, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(kill_event.sequence.all(), **kwargs, many=True)
