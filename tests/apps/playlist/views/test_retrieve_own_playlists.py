from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory

from apps.playlist.models import Playlist

from apps.playlist.serializers import PlaylistListSerializer


class TestRetrieveOwnPlaylists(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.own_playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        self.url = reverse('own_playlists')

    def test_return_own_playlists(self):
        """
        Should verify if it returns the channel's own playlists
        """
        PlaylistFactory.create_batch(2)

        response = self.client.get(self.url)

        retrieve_playlists = [dict(playlist)['id'] for playlist in response.data.get('data')]

        self.assertEqual(len(retrieve_playlists), 1)
        self.assertIn(self.own_playlist.pk, retrieve_playlists)

    def test_return_serialized_own_playlists(self):
        """
        Should verify if it returns the serialized playlists
        """
        serialized_own_playlist = PlaylistListSerializer(self.own_playlist)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            serialized_own_playlist.data,
            response.data.get('data')[0]
        )
