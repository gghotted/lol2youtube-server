from datetime import datetime, timedelta

from rest_framework.generics import (CreateAPIView, RetrieveAPIView,
                                     UpdateAPIView)

from youtube.models import UploadInfo
from youtube.serializers import (CommentADCreateSerializer,
                                 UploadInfoCreateSerializer,
                                 UploadInfoSerializer,
                                 UploadInfoUpdateSerializer)


class UploadInfoWaitUploadView(RetrieveAPIView):
    serializer_class = UploadInfoSerializer

    def get_object(self):
        return UploadInfo.objects.filter(url='').first()


class UploadInfoNotHasADView(RetrieveAPIView):
    serializer_class = UploadInfoSerializer

    def get_object(self):
        upload_complete_time = datetime.now() - timedelta(minutes=3)
        return (UploadInfo.objects
                          .filter(comment_ad=None, created__lte=upload_complete_time)
                          .exclude(channel_name='')
                          .first())


class UploadInfoUpdateView(UpdateAPIView):
    serializer_class = UploadInfoUpdateSerializer
    
    def get_queryset(self):
        return UploadInfo.objects.all()


class UploadInfoCreateView(CreateAPIView):
    serializer_class = UploadInfoCreateSerializer


class CommentADCreateView(CreateAPIView):
    serializer_class = CommentADCreateSerializer
