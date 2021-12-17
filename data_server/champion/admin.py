from django.contrib import admin

from champion.models import Champion


@admin.register(Champion)
class ChampionAdmin(admin.ModelAdmin):
    list_display = (
        'eng_name',
        'kor_name',
        'match_count',
        'kill_count',
        'pentakill_count',
    )
    list_editable = (
        'kor_name',
    )

    def get_ordering(self, request):
        return ('-pentakill_count', )

    @admin.display(ordering='match_count')
    def match_count(self, obj):
        return obj.match_count

    @admin.display(ordering='kill_count')
    def kill_count(self, obj):
        return obj.kill_count
    
    @admin.display(ordering='pentakill_count')
    def pentakill_count(self, obj):
        return obj.pentakill_count
