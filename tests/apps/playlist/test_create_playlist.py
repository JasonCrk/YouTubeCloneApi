from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from apps.playlist.models import Playlist
from apps.playlist.choices import Visibility

from faker import Faker

faker = Faker()


class TestCreatePlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('create_playlist')

    def test_to_return_success_response_if_the_playlist_has_been_created_successfully(self):
        playlist_name = faker.pystr()

        response = self.client.post(
            self.url,
            {
                'name': playlist_name,
                'visibility': Visibility.PRIVATE
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': f'Added to {playlist_name}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_to_check_if_the_playlist_in_private_has_been_created_successfully(self):
        self.client.post(
            self.url,
            {
                'name': faker.pystr(),
                'visibility': Visibility.PRIVATE
            },
            format='json'
        )

        count_channel_playlists = Playlist.objects.filter(channel=self.user.current_channel).count()

        self.assertEqual(count_channel_playlists, 1)

    def test_to_return_error_response_and_status_code_400_if_the_playlist_name_exceeds_150_characters(self):
        response = self.client.post(
            self.url,
            {
                'name': faker.pystr(min_chars=151, max_chars=152),
                'visibility': Visibility.PRIVATE
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('name'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_visibility_does_not_exist_among_the_options(self):
        response = self.client.post(
            self.url,
            {
                'name': faker.pystr(),
                'visibility': faker.pystr()
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('visibility'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
