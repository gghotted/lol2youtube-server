from rest_framework import serializers

from replay.models import KillReplay, ReplayBlackList, ReplayFile


class BlackListCreateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplayBlackList
        fields = ('match', 'msg')


class KillReplayCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    org_file = serializers.FileField()

    class Meta:
        model = KillReplay
        fields = ('event', 'file', 'org_file')

    def create(self, validated_data):
        file = ReplayFile.objects.create(file=validated_data.pop('file'))
        org_file = ReplayFile.objects.create(file=validated_data.pop('org_file'))
        instance = KillReplay.objects.create(
            file=file,
            org_file=org_file,
            **validated_data,
        )
        return instance