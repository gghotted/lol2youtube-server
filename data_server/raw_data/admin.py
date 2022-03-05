from common.filters import AnnotateFieldFilterFactory
from data_cleaner.json_data import JsonDataCleaner
from django.contrib import admin, messages
from django.db.models import BooleanField, Case, Value, When
from django.db.models.expressions import F
from event.models import ChampionKill

from raw_data.models import APIKey, CrawlableMatch, JsonData


@admin.register(JsonData)
class MatchJsonDataAdmin(admin.ModelAdmin):
    list_display = (
        'game_creation',
        'max_kill_length',
        'will_delete',
        'recorded',
    )
    list_filter = (
        AnnotateFieldFilterFactory('will_delete', (True, False)),
        AnnotateFieldFilterFactory('recorded', (True, False)),
        AnnotateFieldFilterFactory('max_kill_length', range(1, 6)),
    )
    actions = (
        'delete_all',
    )

    def get_ordering(self, request):
        return (
            'will_delete',
            '-max_kill_length',
            '-game_creation',
        )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        cleaner = JsonDataCleaner()
        will_delete_ids = cleaner.get_final_queryset().values('id')
        recorded_ids = ChampionKill.objects.all().recorded().values('timeline__match__json__id')
        return cleaner.start_queryset.annotate(
            will_delete=Case(
                When(id__in=will_delete_ids, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            recorded=Case(
                When(id__in=recorded_ids, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )

    @admin.display(ordering='game_creation')
    def game_creation(self, obj):
        return obj.game_creation

    @admin.display(ordering='max_kill_length')
    def max_kill_length(self, obj):
        return obj.max_kill_length

    @admin.display(ordering='will_delete')
    def will_delete(self, obj):
        return obj.will_delete

    @admin.display(ordering='recorded')
    def recorded(self, obj):
        return obj.recorded

    @admin.action(description='선택 항목 삭제')
    def delete_all(self, request, queryset):
        if queryset.filter(will_delete=False).exists():
            self.message_user(request, 'will_delete == True인 항목을 삭제할 수 없습니다.', messages.ERROR)
        else:
            count, detail = queryset.delete()
            self.message_user(request, f'{count}개의 데이터가 삭제되었습니다. {detail}')


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        'key',
    )


@admin.register(CrawlableMatch)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'id',
        'used',
    )
