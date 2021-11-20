from django.contrib import admin

from summoner.models import Summoner


@admin.register(Summoner)
class SummonerAdmin(admin.ModelAdmin):
    list_display = ('name', 'match_updated_at', 'recent_match_at')
    fields = ('name', 'puuid', 'match_updated_at')
    list_per_page = 20
    show_full_result_count = False

    def get_queryset(self, request):
        return self.model.objects.order_by_update_priority()

    def recent_match_at(self, obj):
        return obj.recent_match_at
