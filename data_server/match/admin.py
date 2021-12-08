from django.contrib import admin

from match.models import Version


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'useable',
        'str',
        'first_game_creation',
        'last_game_creation',
        'match_count',
        # 'pentakill_count',
    )
    list_editable = (
        'useable',
    )
    ordering = (
        '-useable',
        '-str',
    )

    def first_game_creation(self, obj):
        return obj.first_game_creation

    def last_game_creation(self, obj):
        return obj.last_game_creation

    def match_count(self, obj):
        return obj.match_count

    # def pentakill_count(self, obj):
    #     return obj.pentakill_count
