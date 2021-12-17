from django.urls import path

from replay import views

app_name = 'replay'

urlpatterns = [
    path('blacklist/', views.BlackListCreateView.as_view(), name='blacklist_create'),
    path('kill/', views.KillReplayCreateView.as_view(), name='kill_create'),
    path('kill/wait-upload', views.KillReplayWaitUploadDetailView.as_view(), name='kill_detail'),
]
