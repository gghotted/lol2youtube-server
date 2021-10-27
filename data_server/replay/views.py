from rest_framework.generics import CreateAPIView

from replay import serializers


class KillReplayCreateView(CreateAPIView):
    serializer_class = serializers.KillReplayCreateSerializer
