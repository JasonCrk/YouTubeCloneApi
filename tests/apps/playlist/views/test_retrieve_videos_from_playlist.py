from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory

from apps.playlist.models import Playlist, PlaylistVideo
from apps.playlist.choices import Visibility

from apps.playlist.serializers import PlaylistVideoListSerializer


class TestRetrieveVideosFromAPlaylist(APITestCaseWithAuth):
    def setUp(self):
        self.url_name = 'videos_from_a_playlist'

    def test_the_playlist_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the playlist does not exist
        """
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})
        
        playlist.delete()

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})

    def test_return_the_videos_from_a_playlist(self):
        """
        Should return the videos from a playlist successfully
        """
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        playlist_videos = PlaylistVideoFactory.create_batch(2, playlist=playlist)
        video = PlaylistVideoFactory.create()

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        retrieved_playlist_videos_ids = [dict(video)['id'] for video in response.data.get('data')]

        self.assertIn(playlist_videos[0].pk, retrieved_playlist_videos_ids)
        self.assertIn(playlist_videos[1].pk, retrieved_playlist_videos_ids)

        self.assertNotIn(video.pk, retrieved_playlist_videos_ids)

    def test_serialized_playlist_videos_list(self):
        """
        Should return a serialized playlist videos list from a playlist
        """
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=playlist)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        serialized_playlist_video = PlaylistVideoListSerializer(playlist_video)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data.get('data')[0],
            serialized_playlist_video.data
        )

    def test_the_playlist_is_PRIVATE_and_not_authenticated(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the videos from a PRIVATE playlist and i am not authenticated
        """
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PRIVATE)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertDictEqual(response.data, {'message': 'You are not authorized to view this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_the_playlist_is_PRIVATE_and_not_owned_by_you(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the videos from a PRIVATE playlist and not owned by you
        """
        super().setUp()

        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PRIVATE)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertDictEqual(response.data, {'message': 'You are not authorized to view this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_the_playlist_is_PRIVATE_but_i_am_authenticated_and_its_mine(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the videos from a PRIVATE playlist and I am authenticated and it's mine
        """
        super().setUp()

        playlist: Playlist = PlaylistFactory.create(
            visibility=Visibility.PRIVATE,
            channel=self.user.current_channel
        )

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertIsInstance(response.data.get('data'), list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
