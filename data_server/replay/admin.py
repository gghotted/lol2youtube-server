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
        if not obj.file:
            return None
        return mark_safe(
            f'<video controls width="400" preload="metadata">'
            f'<source src="{obj.file.file.url}" type="video/mp4">'
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
