from rest_framework import serializers

from replay.models import KillReplay, ReplayBlackList, ReplayFile


class BlackListCreateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplayBlackList
        fields = ('match', 'msg')


class KillReplayCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False)
    org_file = serializers.FileField()

    class Meta:
        model = KillReplay
        fields = ('event', 'file', 'org_file')

    def create(self, validated_data):
        org_file = ReplayFile.objects.create(file=validated_data.pop('org_file'))
        params = {
            **validated_data,
            'org_file': org_file,
        }
        if validated_data.get('file'):
            params['file'] = ReplayFile.objects.create(file=validated_data.pop('file'))
        instance = KillReplay.objects.create(**validated_data)
        return instance
