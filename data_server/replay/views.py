from rest_framework.generics import (CreateAPIView, RetrieveAPIView,
                                     UpdateAPIView)

from replay import serializers
from replay.models import KillReplay


class BlackListCreateView(CreateAPIView):
    serializer_class = serializers.BlackListCreateCreateSerializer


class KillReplayCreateView(CreateAPIView):
    serializer_class = serializers.KillReplayCreateSerializer


class KillReplayWaitUploadDetailView(RetrieveAPIView):
    serializer_class = serializers.KillReplaySerializer

    def get_object(self):
        return KillReplay.objects.has_both_file().order_by('?').first()
