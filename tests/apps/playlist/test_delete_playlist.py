from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory

from apps.playlist.models import Playlist


class TestDeletePlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)
        self.url_name = 'delete_playlist'
        self.url = reverse(self.url_name, kwargs={'playlist_id': self.playlist.pk})

    def test_playlist_does_not_exist(self):
        """
        Should return an error message if the playlist does not exist
        """
        self.playlist.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_channel_wants_to_delete_a_playlist_it_does_not_own(self):
        """
        Should return an error message and 401 status code
        if a channels wants to delete a playlist it does not own
        """
        not_own_playlist: Playlist = PlaylistFactory.create()

        url = reverse(self.url_name, kwargs={'playlist_id': not_own_playlist.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'You are not the owner of this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_message_response(self):
        """
        Should return an success message and 200 status code
        if the playlist has been deleted successfully
        """
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The playlist has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_that_the_playlist_has_been_deleted(self):
        """
        Should verify that the playlist has been deleted from the database
        """
        self.client.delete(self.url)

        playlist_deleted = Playlist.objects.filter(id=self.playlist.pk)

        self.assertFalse(playlist_deleted.exists())
