from django.contrib import admin, messages
from youtube.models import UploadInfo

from replay.filters import KillReplayFilter
from replay.forms import SelectKillLongReplayActionForm
from replay.models import (KillLongReplay, KillReplay, ReplayBlackList,
                           ReplayFile)


class UploadInfoInline(admin.StackedInline):
    model = UploadInfo


@admin.register(ReplayFile)
class ReplayFileAdmin(admin.ModelAdmin):
    inlines = (
        UploadInfoInline,
    )
    fields = (
        'file',
    )


@admin.register(KillReplay)
class KillReplayAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'duration',
    )
    fields = (
        'org_file',
        'file',
        'long_file',
    )
    readonly_fields = (
        'org_file',
        'long_file',
    )
    list_filter = (
        KillReplayFilter,
    )
    action_form = SelectKillLongReplayActionForm
    actions = (
        'add_long_file',
    )

    def get_ordering(self, request):
        return (
            'event__duration',
        )

    @admin.display(ordering='event__duration')
    def duration(self, obj):
        return obj.event.duration

    @admin.action(description='선택된 항목을 긴 영상(모음집)과 연결')
    def add_long_file(self, request, queryset):
        long_replay_id = int(request.POST.get('kill_long_replay', -1))
        if long_replay_id == -1:
            self.message_user(request, '긴 영상이 선택되지 않았습니다', messages.ERROR)
            return 
        updated = queryset.update(long_file=long_replay_id)
        self.message_user(request, updated)



@admin.register(KillLongReplay)
class KillLongReplayAdmin(admin.ModelAdmin):
    fields = (
        'file',
    )


@admin.register(ReplayBlackList)
class BlackListAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'msg',
    )
    ordering = (
        '-created',
    )
