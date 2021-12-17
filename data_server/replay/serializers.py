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
        instance = KillReplay.objects.create(**params)
        return instance


class KillReplaySerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    filepath = serializers.SerializerMethodField()

    class Meta:
        model = KillReplay
        fields = ('id', 'file', 'title', 'description', 'filepath')

    def get_title(self, obj):
        return obj.title

    def get_description(self, obj):
        return obj.description

    def get_filepath(self, obj):
        return obj.file.file.path
