from rest_framework.generics import RetrieveAPIView

from youtube.models import UploadInfo
from youtube.serializers import UploadInfoSerializer


class UploadInfoWaitUploadView(RetrieveAPIView):
    serializer_class = UploadInfoSerializer

    def get_object(self):
        return UploadInfo.objects.filter(url='').first()
