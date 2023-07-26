from django.urls import path

from apps.video import views

urlpatterns = [
    path('create/', views.CreateVideoView.as_view(), name='upload_video'),
    path('like/', views.LikeVideoView.as_view(), name='like_video'),
    path('dislike/', views.DislikeVideoView.as_view(), name='dislike_video'),
    path('<int:video_id>/edit/', views.EditVideoView.as_view(), name='edit_video'),
    path('<int:video_id>/delete/', views.DeleteVideoView.as_view(), name='delete_video')
]