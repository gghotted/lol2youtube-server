from rest_framework import serializers

from event.models import ChampionKill


class NotRecordedChampionKillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChampionKill
        fields = '__all__'
