from rest_framework import serializers

from youtube.models import UploadInfo


class UploadInfoSerializer(serializers.ModelSerializer):
    filepath = serializers.SerializerMethodField()

    class Meta:
        model = UploadInfo
        fields = (
            'id',
            'title',
            'description',
            'filepath',
        )
    
    def get_filepath(self, obj):
        return obj.file.file.path
