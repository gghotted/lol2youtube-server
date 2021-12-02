import requests
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View

from youtube.models import Channel


class YoutubeCallbackView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET['code']
        url = 'https://accounts.google.com/o/oauth2/token'
        data = {
            'code': code,
            'client_id': settings.YOUTUBE_CLIENT_ID,
            'client_secret': settings.YOUTUBE_CLIENT_SECRET,
            'redirect_uri': settings.YOUTUBE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        res = requests.post(url, data=data).json()

        channel = Channel.objects.get(pk=request.session['channel_obj_pk'])
        channel.access_token = res['access_token']
        channel.refresh_token = res['refresh_token']
        channel.save()

        return redirect('/admin/youtube/channel/')
