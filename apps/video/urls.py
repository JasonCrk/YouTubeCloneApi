from django.urls import path

from apps.video import views

urlpatterns = [
    path('create/', views.CreateVideoView.as_view(), name='upload_video'),
    path('like/', views.LikeAndDislikeVideoView.as_view(), name='like_dislike_video')
]