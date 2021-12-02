from django.contrib.admin import SimpleListFilter

from replay.models import KillReplay


class KillReplayFilter(SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('non_status', '상태 없음'),
            ('wait_upload', '업로드 대기중'),
            ('uploaded', '업로드 됨'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val:
            return getattr(KillReplay.objects, val)()
