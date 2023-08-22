from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory

from apps.playlist.models import Playlist
from apps.playlist.choices import Visibility
from apps.playlist.serializers import PlaylistDetailsSerializer


class TestRetrievePlaylistDetails(APITestCaseWithAuth):
    def setUp(self):
        self.url_name = 'playlist_details'

    def test_return_the_playlist(self):
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertEqual(response.data.get('id'), playlist.pk)

    def test_return_serialized_playlist_details(self):
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        serialized_playlist = PlaylistDetailsSerializer(playlist)

        self.assertEqual(response.data, serialized_playlist.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_playlist_does_not_exist(self):
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        playlist.delete()

        response = self.client.get(url)

        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_the_playlist_is_PRIVATE_and_not_authenticated(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the playlist details from a PRIVATE playlist and he doesn't authenticated
        """
        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PRIVATE)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertDictEqual(response.data, {'message': 'You are not authorized to view this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_the_playlist_is_PRIVATE_and_not_owned_by_you(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the playlist details from a PRIVATE playlist and not owned by you
        """
        super().setUp()

        playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PRIVATE)

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertDictEqual(response.data, {'message': 'You are not authorized to view this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_the_playlist_is_PRIVATE_but_he_is_authenticated_and_its_yours(self):
        """
        Should return an error response and a 401 status code if a channel wants to retrieve the playlist details from a PRIVATE playlist and he is authenticated and it's yours
        """
        super().setUp()

        playlist: Playlist = PlaylistFactory.create(
            visibility=Visibility.PRIVATE,
            channel=self.user.current_channel
        )

        url = reverse(self.url_name, kwargs={'playlist_id': playlist.pk})

        response = self.client.get(url)

        self.assertEqual(response.data.get('id'), playlist.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
