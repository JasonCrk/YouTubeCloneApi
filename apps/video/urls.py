from django.urls import path

from apps.video import views

urlpatterns = [
    path('channel/<int:channel_id>/', views.RetrieveChannelVideosView.as_view(), name='channel_videos'),
    path('search/', views.SearchVideosView.as_view(), name='search_videos'),
    path('create/', views.CreateVideoView.as_view(), name='upload_video'),
    path('like/', views.LikeVideoView.as_view(), name='like_video'),
    path('dislike/', views.DislikeVideoView.as_view(), name='dislike_video'),
    path('<int:video_id>/', views.RetrieveVideoDetailsView.as_view(), name='video_details'),
    path('<int:video_id>/viewed/', views.AddVisitToVideoView.as_view(), name='visit_to_video'),
    path('<int:video_id>/edit/', views.EditVideoView.as_view(), name='edit_video'),
    path('<int:video_id>/delete/', views.DeleteVideoView.as_view(), name='delete_video')
]