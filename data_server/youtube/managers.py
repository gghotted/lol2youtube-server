from common.models import BaseManager


class UploadInfoManager(BaseManager):
    def wait_upload(self):
        return self.get_queryset().filter(url='')

    def uploaded(self):
        return self.get_queryset().exclude(url='')
