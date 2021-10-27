from django.urls import path

from replay import views

app_name = 'replay'

urlpatterns = [
    path('kill/', views.KillReplayCreateView.as_view(), name='kill_create')
]
