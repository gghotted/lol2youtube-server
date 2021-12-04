from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from replay.filters import KillReplayFilter
from replay.models import KillReplay


@admin.register(KillReplay)
class KillReplayAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = (
        'id',
        'created',
        'video',
        'channel_group',
        'channel',
        'url',
    )
    fields = (
        'id',
    )
    readonly_fields = (
        'event',
    )
    list_per_page = 10
    list_filter = (
        KillReplayFilter,
    )
    ordering = (
        '-created',
    )
    actions = (
        'set_wait_upload',
    )

    @admin.display()
    def video(self, obj):
        return mark_safe(
            f'<video controls width="400" preload="none">'
            f'<source src="{obj.file.file.url}" type="video/webm">'
            f'</video>'
        )

    def channel_group(self, obj):
        try:
            return obj.file.upload_info.channel_group
        except:
            return None

    def channel(self, obj):
        try:
            return obj.file.upload_info.channel
        except:
            return None

    def url(self, obj):
        try:
            return mark_safe('<a href="{url}">{url}</a>'.format(url=obj.file.upload_info.url))
        except:
            return None

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='"업로드 대기중"으로 상태 변경')
    def set_wait_upload(self, request, queryset):
        selected = set(queryset.values_list('id', flat=True))
        all = set(KillReplay.objects.non_status().values_list('id', flat=True))
        if len(selected - all) != 0:
            self.message_user(request, '상태 없음이 아닌 데이터가 포함되었습니다.', messages.ERROR)
            return
        for obj in queryset:
            obj.set_wait_upload()
