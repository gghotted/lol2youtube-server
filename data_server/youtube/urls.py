from django.urls import path

from youtube import views

app_name = 'youtube'

urlpatterns = [
    path('upload_info/wait_upload', views.UploadInfoWaitUploadView.as_view()),
    path('upload_info/not_has_ad', views.UploadInfoNotHasADView.as_view()),
    path('upload_info/<int:pk>', views.UploadInfoUpdateView.as_view()),
    path('upload_info', views.UploadInfoCreateView.as_view()),
    path('commentad', views.CommentADCreateView.as_view()),
]
