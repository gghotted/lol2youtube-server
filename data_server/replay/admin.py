from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from replay.models import KillReplay


@admin.register(KillReplay)
class KillReplayAdmin(admin.ModelAdmin):
    show_full_result_count = False
    list_display = (
        'id',
        'created',
        'video',
        'upload_status'
    )
    fields = (
        'id',
    )
    readonly_fields = (
        'event',
    )
    list_per_page = 10
    list_filter = (
        'upload_status',
    )
    list_editable = (
        'upload_status',
    )
    ordering = (
        '-created',
    )

    @admin.display()
    def video(self, obj):
        return mark_safe(
            f'<video controls width="400" preload="none">'
            f'<source src="{obj.file.url}" type="video/webm">'
            f'</video>'
        )

    def save_model(self, request, obj, form, change):
        if obj.upload_status == '업로드됨':
            self.message_user(request, f'{obj.id}의 상태를 "업로드됨"으로 수동 업데이트할 수 없음', messages.ERROR)
        else:
            super().save_model(request, obj, form, change)
