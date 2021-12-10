from common.models import BaseManager


class ReplaySourceManager(BaseManager):
    # 상태 없음
    def non_status(self):
        return self.get_queryset().filter(org_file__upload_info=None)

    # 업로드 대기중
    def wait_upload(self):
        return (self.get_queryset()
                    .exclude(org_file__upload_info=None)
                    .filter(org_file__upload_info__url=''))

    # 업로드 됨
    def uploaded(self):
        return (self.get_queryset()
                    .exclude(org_file__upload_info=None)
                    .exclude(org_file__upload_info__url=''))
