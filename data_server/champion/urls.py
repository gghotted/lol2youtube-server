from django.urls import path

from champion.views import MaxPentakillChampionView

app_name = 'champion'

urlpatterns = [
    path('maxPentakill', MaxPentakillChampionView.as_view(), name='max_pentakill'),
]
