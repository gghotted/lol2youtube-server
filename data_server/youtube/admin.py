from urllib.parse import urlencode

from django.conf import settings
from django.contrib import admin
from django.db.models.aggregates import Count
from django.shortcuts import redirect

from youtube.models import Channel, ChannelGroup


@admin.register(ChannelGroup)
class ChannelGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    readonly_fields = (
        'access_token',
        'refresh_token',
    )
    list_display = (
        'name',
        'group',
        'uploaded',
    )

    def uploaded(self, obj):
        return obj.uploaded

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            uploaded=Count('upload_infos')
        )

    def response_add(self, request, obj, post_url_continue=None):
        request.session['channel_obj_pk'] = obj.pk
        query = {
            'client_id': settings.YOUTUBE_CLIENT_ID,
            'redirect_uri': settings.YOUTUBE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'https://www.googleapis.com/auth/youtube.upload',
            'access_type': 'offline',
        }
        url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(query)
        return redirect(url)
