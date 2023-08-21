from django.urls import path

from apps.playlist import views

urlpatterns = [
    path(
        'own/',
        views.RetrieveOwnPlaylistsView.as_view(),
        name='own_playlists'
    ),
    path(
        'create/',
        views.CreatePlaylistView.as_view(),
        name='create_playlist'
    ),
    path(
        'channel/<int:channel_id>',
        views.RetrieveChannelPlaylistsView.as_view(),
        name='channel_playlists'
    ),
    path(
        '<int:playlist_id>/videos',
        views.RetrieveVideosFromAPlaylist.as_view(),
        name='videos_from_a_playlist'
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