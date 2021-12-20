from rest_framework import serializers

from youtube.models import CommentAD, UploadInfo


class UploadInfoSerializer(serializers.ModelSerializer):
    filepath = serializers.SerializerMethodField()

    class Meta:
        model = UploadInfo
        fields = (
            'id',
            'title',
            'description',
            'filepath',
            'url',
        )
    
    def get_filepath(self, obj):
        return obj.file.file.path


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
        )


class CommentADCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentAD
        fields = (
            'upload_info',
            'content',
        )
