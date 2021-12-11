from django.contrib.admin import SimpleListFilter

from replay.models import KillReplay


class KillReplayFilter(SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('has_only_org_file', '원본 파일만 있음'),
            ('has_both_file', '업로드 파일 생성됨'),
            ('has_upload_info', '업로드 됨(긴 영상 없음)'),
            ('has_long_file', '업로드 됨(긴 영상 있음)'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            return getattr(KillReplay.objects, val)()
