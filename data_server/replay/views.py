from rest_framework.generics import CreateAPIView, UpdateAPIView

from replay import serializers
from replay.models import KillReplay


class BlackListCreateView(CreateAPIView):
    serializer_class = serializers.BlackListCreateCreateSerializer


class KillReplayCreateView(CreateAPIView):
    serializer_class = serializers.KillReplayCreateSerializer


class KillReplayUpdateView(UpdateAPIView):
    serializer_class = serializers.KillReplayUpdateSerializer

    def get_object(self):
        match = self.kwargs.get('match')
        return KillReplay.objects.get(match=match)
