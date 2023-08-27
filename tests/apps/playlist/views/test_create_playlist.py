from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from apps.playlist.models import Playlist
from apps.playlist.choices import Visibility

from apps.playlist.serializers import PlaylistListSimpleSerializer

from faker import Faker

faker = Faker()


class TestCreatePlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('create_playlist')

    def test_return_a_serialized_playlist(self):
        """
        Should return a serialized playlist
        """
        playlist_name = faker.pystr()

        response = self.client.post(
            self.url,
            {
                'name': playlist_name,
                'visibility': Visibility.PRIVATE
            },
            format='json'
        )

        playlist = Playlist.objects.filter(name=playlist_name).first()

        serialized_playlist = PlaylistListSimpleSerializer(playlist)

        self.assertDictEqual(response.data, dict(serialized_playlist.data))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_playlist_has_been_created(self):
        """
        Should verify if the playlist has been created successfully
        """
        self.client.post(
            self.url,
            {
                'name': faker.pystr(),
                'visibility': Visibility.PRIVATE
            },
            format='json'
        )

        channel_playlist = Playlist.objects.filter(channel=self.user.current_channel)

        self.assertEqual(channel_playlist.count(), 1)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.post(
            self.url,
            {
                'name': faker.pystr(min_chars=151, max_chars=152),
                'visibility': faker.pystr()
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('name', response.data.get('errors'))
        self.assertIn('visibility', response.data.get('errors'))
