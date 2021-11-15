from rest_framework.generics import CreateAPIView

from replay import serializers


class BlackListCreateView(CreateAPIView):
    serializer_class = serializers.BlackListCreateCreateSerializer


class KillReplayCreateView(CreateAPIView):
    serializer_class = serializers.KillReplayCreateSerializer
