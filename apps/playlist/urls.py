from django.urls import path

from apps.playlist import views

urlpatterns = [
    path(
        'create/',
        views.CreatePlaylistView.as_view(),
        name='create_playlist'
    ),
    path(
        '<int:playlist_id>/save-video/',
        views.SaveVideoToPlaylistView.as_view(),
        name='save_video_to_playlist'
    ),
    path(
        '<int:playlist_id>/edit/',
        views.EditPlaylistView.as_view(),
        name='edit_playlist'
    ),
    path(
        '<int:playlist_id>/delete/',
        views.DeletePlaylistView.as_view(),
        name='delete_playlist'
    ),
    path(
        'video/<int:playlist_video_id>/remove',
        views.RemoveVideoFromPlaylistView.as_view(),
        name='remove_video_from_playlist'
    )
]