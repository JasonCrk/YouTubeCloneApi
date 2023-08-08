from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory

from apps.playlist.models import Playlist
from apps.playlist.choices import Visibility

from faker import Faker

faker = Faker()


class TestEditPlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.test_playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)
        self.url_name = 'edit_playlist'
        self.url = reverse(self.url_name, kwargs={'playlist_id': self.test_playlist.pk})

    def test_to_return_success_response_if_the_playlist_has_been_updated_successfully(self):
        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(),
                'description': faker.paragraph(),
                'visibility': Visibility.PUBLIC.value
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Playlist updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_playlist_name_has_been_updated_successfully(self):
        new_playlist_name = faker.pystr()

        self.client.patch(
            self.url,
            {
                'name': new_playlist_name,
            },
            format='json'
        )

        test_playlist_updated = Playlist.objects.get(id=self.test_playlist.pk)

        self.assertEqual(new_playlist_name, test_playlist_updated.name)

    def test_to_check_if_the_playlist_description_has_been_updated_successfully(self):
        new_playlist_description = faker.paragraph()

        self.client.patch(
            self.url,
            {
                'description': new_playlist_description,
            },
            format='json'
        )

        test_playlist_updated = Playlist.objects.get(id=self.test_playlist.pk)

        self.assertEqual(new_playlist_description, test_playlist_updated.description)

    def test_to_check_if_the_playlist_visibility_has_been_updated_successfully(self):
        new_playlist_visibility = Visibility.PUBLIC.value

        self.client.patch(
            self.url,
            {
                'visibility': new_playlist_visibility,
            },
            format='json'
        )

        test_playlist_updated = Playlist.objects.get(id=self.test_playlist.pk)

        self.assertEqual(new_playlist_visibility, test_playlist_updated.visibility)

    def test_to_return_error_response_and_status_code_404_if_the_playlist_does_not_exists(self):
        self.test_playlist.delete()

        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(),
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_401_if_a_channel_wants_to_edit_a_playlist_that_he_does_not_own(self):
        not_own_playlist = PlaylistFactory.create()

        url = reverse(self.url_name, kwargs={'playlist_id': not_own_playlist.pk})

        response = self.client.patch(
            url,
            {
                'name': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_and_status_code_400_if_the_playlist_name_exceeds_150_characters(self):
        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(min_chars=151, max_chars=152)
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('name'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
