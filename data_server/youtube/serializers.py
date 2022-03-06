from rest_framework import serializers

from youtube.models import CommentAD, UploadInfo


class UploadInfoSerializer(serializers.ModelSerializer):
    filepath = serializers.SerializerMethodField()
    ad_comment = serializers.SerializerMethodField()

    class Meta:
        model = UploadInfo
        fields = (
            'id',
            'title',
            'description',
            'filepath',
            'url',
            'channel_name',
        )
    
    def get_filepath(self, obj):
        return obj.file.file.path

    def get_ad_comment(self, obj):
        return obj.file.replay.ad_comment


class UploadInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadInfo
        fields = (
            'url',
        )


class UploadInfoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadInfo
        fields = (
            'file',
            'title',
            'description',
            'url',
            'channel_name',
        )


class CommentADCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentAD
        fields = (
            'upload_info',
            'content',
        )
