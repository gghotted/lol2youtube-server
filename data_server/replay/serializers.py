from rest_framework import serializers

from replay.models import KillReplay


class KillReplayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KillReplay
        fields = ('file', 'event')
