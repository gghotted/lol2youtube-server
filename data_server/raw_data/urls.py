from django.urls import path

from raw_data import views

urlpatterns = [
    path('crawlablematch', views.CrawlableMatchCreateView.as_view())
]
