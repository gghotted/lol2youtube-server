from rest_framework import serializers

from replay.models import KillReplay, ReplayBlackList, ReplayFile


class BlackListCreateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplayBlackList
        fields = ('match', 'msg')


class KillReplayCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = KillReplay
        fields = ('file', 'event')

    def create(self, validated_data):
        file = ReplayFile.objects.create(file=validated_data.pop('file'))
        instance = KillReplay.objects.create(
            file=file,
            **validated_data,
        )
        return instance
