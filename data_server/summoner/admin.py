from django.contrib import admin

from summoner.models import Summoner


@admin.register(Summoner)
class SummonerAdmin(admin.ModelAdmin):
    list_display = ('name', 'match_updated_at', 'recent_match_at')

    def get_queryset(self, request):
        return self.model.objects.order_by_update_priority()

    def recent_match_at(self, obj):
        return obj.recent_match_at
