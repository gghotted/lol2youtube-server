from rest_framework.generics import RetrieveAPIView, UpdateAPIView

from youtube.models import UploadInfo
from youtube.serializers import (UploadInfoSerializer,
                                 UploadInfoUpdateSerializer)


class UploadInfoWaitUploadView(RetrieveAPIView):
    serializer_class = UploadInfoSerializer

    def get_object(self):
        return UploadInfo.objects.filter(url='').first()


class UploadInfoUpdateView(UpdateAPIView):
    serializer_class = UploadInfoUpdateSerializer
    
    def get_queryset(self):
        return UploadInfo.objects.all()
