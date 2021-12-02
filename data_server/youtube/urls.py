from django.urls import path

from youtube.views import YoutubeCallbackView

app_name = 'youtube'

urlpatterns = [
    path('callback/', YoutubeCallbackView.as_view(), name='callback'),
]
