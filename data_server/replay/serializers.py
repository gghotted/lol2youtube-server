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
    file_url = serializers.SerializerMethodField()
    org_file_url = serializers.SerializerMethodField()

    class Meta:
        model = KillReplay
        fields = ('id', 'file', 'title', 'description', 'filepath', 'file_url', 'org_file_url')

    def get_title(self, obj):
        return obj.title

    def get_description(self, obj):
        return obj.description

    def get_filepath(self, obj):
        if obj.file:
            return obj.file.file.path
        else:
            return None
    
    def get_org_file_url(self, obj):
        request = self.context['request']
        return request.build_absolute_uri(obj.org_file.file.url)

    def get_file_url(self, obj):
        request = self.context['request']
        if obj.file:
            return request.build_absolute_uri(obj.file.file.url)
        return ''


class KillReplayUpdateSerializer(serializers.ModelSerializer):
    shorts_file = serializers.FileField(write_only=True)

    class Meta:
        model = KillReplay
        fields = ('shorts_file', 'ad_comment')
    
    def update(self, instance, validated_data):
        instance.file = ReplayFile.objects.create(file=validated_data['shorts_file'])
        instance.ad_comment = validated_data.get('ad_comment', '')
        instance.save()
        return instance
