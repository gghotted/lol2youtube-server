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
        'event',
        'video',
        'title',
        'url',
    )
    fields = (
        'id',
        'file',
        'org_file',
        'event',
    )
    readonly_fields = (
        'id',
        'file',
        'org_file',
        'event',
    )
    list_per_page = 5
    list_filter = (
        KillReplayFilter,
    )
    ordering = (
        '-created',
    )
    actions = (
        'blacklist_queryset',
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

    def url(self, obj):
        try:
            return mark_safe('<a href="{url}">{url}</a>'.format(url=obj.file.upload_info.url))
        except:
            return None

    def title(self, obj):
        try:
            return obj.file.upload_info.title
        except:
            return None

    def delete_model(self, request, obj):
        if not obj.deleteable():
            self.message_user(request, f'{obj}를 삭제할 수 없습니다', messages.ERROR)
            return
        obj.delete()
        self.message_user(request, f'{obj}를 삭제했습니다')
        

    def delete_queryset(self, request, queryset):
        '''
        삭제 후 다시 크롤링될 수 있습니다.
        '''
        for obj in queryset:
            self.delete_model(request, obj)

    def blacklist_model(self, request, obj):
        if not obj.deleteable():
            self.message_user(request, f'{obj}를 삭제할 수 없습니다', messages.ERROR)
            return
        obj.to_blacklist()
        self.message_user(request, f'{obj}를 삭제했습니다')

    @admin.action(description='삭제 및 블랙리스트에 등록')
    def blacklist_queryset(self, request, queryset):
        '''
        삭제 후 다시 크롤링될 수 없습니다.
        '''
        for obj in queryset:
            obj.to_blacklist()

    @admin.action(description='"업로드 대기중"으로 상태 변경')
    def set_wait_upload(self, request, queryset):
        selected = set(queryset.values_list('id', flat=True))
        all = set(KillReplay.objects.non_status().values_list('id', flat=True))
        if len(selected - all) != 0:
            self.message_user(request, '상태 없음이 아닌 데이터가 포함되었습니다.', messages.ERROR)
            return
        for obj in queryset:
            obj.set_wait_upload()

