from django.urls import path

from apps.video import views

urlpatterns = [
    path('search/', views.SearchVideosView.as_view(), name='search_videos'),
    path('create/', views.CreateVideoView.as_view(), name='upload_video'),
    path('trending/', views.RetrieveTrendingVideosView.as_view(), name='trending_videos'),
    path('channel/<int:channel_id>/', views.RetrieveChannelVideosView.as_view(), name='channel_videos'),
    path('<int:video_id>/', views.RetrieveVideoDetailsView.as_view(), name='video_details'),
    path('<int:video_id>/suggestions/', views.RetrieveSuggestionVideosView.as_view(), name='suggestion_videos'),
    path('<int:video_id>/like/', views.LikeVideoView.as_view(), name='like_video'),
    path('<int:video_id>/dislike/', views.DislikeVideoView.as_view(), name='dislike_video'),
    path('<int:video_id>/viewed/', views.AddVisitToVideoView.as_view(), name='visit_to_video'),
    path('<int:video_id>/edit/', views.EditVideoView.as_view(), name='edit_video'),
    path('<int:video_id>/delete/', views.DeleteVideoView.as_view(), name='delete_video')
]
