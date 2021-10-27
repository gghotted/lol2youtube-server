from django.urls import path

from replay import views

app_name = 'replay'

urlpatterns = [
    path('', views.KillReplayCreateView.as_view(), name='kill_create')
]
