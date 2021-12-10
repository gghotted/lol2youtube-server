from match.serializers import ParticipantSerializer
from rest_framework import serializers

from event.models import ChampionKill


class NotRecordedChampionKillSerializer(serializers.ModelSerializer):
    killer = ParticipantSerializer()

    class Meta:
        model = ChampionKill
        fields = (
            'id',
            'timeline',
            'time',
            'killer',
            'start',
        )
