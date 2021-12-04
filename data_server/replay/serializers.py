from rest_framework import serializers

from replay.models import KillReplay, ReplayBlackList, ReplayFile


class BlackListCreateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplayBlackList
        fields = ('match', 'msg')


class KillReplayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KillReplay
        fields = ('event', )


class KillReplayUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = KillReplay
        fields = ('link', )
