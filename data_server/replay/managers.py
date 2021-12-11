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

    '''
    org_file: 소스 원본
    file: 업로드할 파일
    '''

    '''
    org_file만 있음 (org_file은 항상 있음)
    '''
    def has_only_org_file(self):
        return self.filter(file=None)
    
    '''
    두 파일 모두 있음
    단, file의 upload_info == None
    '''
    def has_both_file(self):
        return (self.exclude(file=None)
                    .filter(file__upload_info=None))

    
    '''
    두 파일 모두 있음, 긴 영상 없음
    file의 upload_info != None
    '''
    def has_upload_info(self):
        return (self.exclude(file=None)
                    .exclude(file__upload_info=None)
                    .filter(long_file=None))

    def has_long_file(self):
        return (self.exclude(file=None)
                    .exclude(file__upload_info=None)
                    .exclude(long_file=None))
    
