from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('not-recorded/', views.NotRecordedChampionKillDetailView.as_view(), name='detail_not_recorded'),
]
