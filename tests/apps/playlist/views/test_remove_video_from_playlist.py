from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory
from tests.factories.video import VideoFactory

from apps.playlist.models import Playlist, PlaylistVideo
from apps.video.models import Video


class TestRemoveVideoFromPlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)
        self.video: Video = VideoFactory.create(channel=self.user.current_channel)
        self.playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist, video=self.video)

        self.playlist.video_thumbnail = self.playlist_video
        self.playlist.save()

        self.url_name = 'remove_video_from_playlist'
        self.url = reverse(
            self.url_name,
            kwargs={'video_id': self.video.pk, 'playlist_id': self.playlist.id}
        )

    def test_success_response(self):
        """
        Should return a success response if the video has been removed from the playlist
        """
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': f'Removed from {self.playlist.name}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_video_has_been_removed_from_the_playlist(self):
        """
        Should verify if the video has been removed from the playlist successfully
        """
        self.client.delete(self.url)

        playlist_video_removed = PlaylistVideo.objects.filter(id=self.playlist_video.pk)

        self.assertFalse(playlist_video_removed.exists())

    def test_playlist_updates_its_updated_at(self):
        """
        Should verify if the playlist updates its updated_at field
        """
        self.client.delete(self.url)

        playlist_updated = Playlist.objects.get(id=self.playlist.pk)

        self.assertNotEqual(self.playlist.updated_at, playlist_updated.updated_at)

    def test_playlist_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the playlist video does not exist
        """
        self.playlist_video.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The playlist video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_another_channel_wants_to_remove_a_video_from_a_playlist_it_does_not_own(self):
        """
        Should return an error response and a 401 status code if the another channel wants to remove a video from playlist it does not own
        """
        not_own_playlist_video: PlaylistVideo = PlaylistVideoFactory.create()

        not_own_playlist_video_url = reverse(
            self.url_name,
            kwargs={
                'playlist_id': not_own_playlist_video.playlist.pk,
                'video_id': not_own_playlist_video.video.pk
            }
        )

        response = self.client.delete(not_own_playlist_video_url)

        self.assertDictEqual(response.data, {'message': "You can't remove a video from a playlist that you don't own"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
