from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory

from apps.playlist.models import Playlist, PlaylistVideo
from apps.playlist.choices import Visibility

from faker import Faker

faker = Faker()


class TestEditPlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        self.url_name = 'edit_playlist'
        self.url = reverse(self.url_name, kwargs={'playlist_id': self.playlist.pk})

    def test_success_response(self):
        """
        Should return a success response if the playlist has been updated
        """
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

    def test_playlist_name_has_been_updated(self):
        """
        Should verify if the playlist name has been updated
        """
        new_playlist_name = faker.pystr()

        self.client.patch(
            self.url,
            {
                'name': new_playlist_name,
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(id=self.playlist.pk)

        self.assertEqual(new_playlist_name, playlist_updated.name)

    def test_playlist_description_has_been_updated(self):
        """
        Should verify if the playlist description has been updated successfully
        """
        new_playlist_description = faker.paragraph()

        self.client.patch(
            self.url,
            {
                'description': new_playlist_description,
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(id=self.playlist.pk)

        self.assertEqual(new_playlist_description, playlist_updated.description)

    def test_playlist_visibility_has_been_updated(self):
        new_playlist_visibility = Visibility.PUBLIC.value

        self.client.patch(
            self.url,
            {
                'visibility': new_playlist_visibility,
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(id=self.playlist.pk)

        self.assertEqual(new_playlist_visibility, playlist_updated.visibility)

    def test_playlist_thumbnail_has_been_updated(self):
        self.playlist.video_thumbnail = PlaylistVideoFactory.create(playlist=self.playlist)
        self.playlist.save()

        new_playlist_video = PlaylistVideoFactory.create(playlist=self.playlist)

        self.client.patch(
            self.url,
            {
                'video_thumbnail': new_playlist_video.id,
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(id=self.playlist.pk)

        self.assertEqual(new_playlist_video, playlist_updated.video_thumbnail)

    def test_playlist_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the playlist does not exist
        """
        self.playlist.delete()

        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(),
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_channel_wants_to_edit_a_playlist_it_does_not_own(self):
        """
        Should return an error response and a 401 status code if a channel wants to edit a playlist it does not own
        """
        not_own_playlist = PlaylistFactory.create()

        not_own_playlist_url = reverse(self.url_name, kwargs={'playlist_id': not_own_playlist.pk})

        response = self.client.patch(
            not_own_playlist_url,
            {
                'name': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        self.playlist.video_thumbnail = PlaylistVideoFactory.create(playlist=self.playlist)
        self.playlist.save()

        new_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        non_exist_playlist_video_id = new_playlist_video.pk

        new_playlist_video.delete()

        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(min_chars=151, max_chars=152),
                'visibility': faker.pystr(),
                'video_thumbnail': non_exist_playlist_video_id
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('name', response.data.get('errors'))
        self.assertIn('visibility', response.data.get('errors'))
        self.assertIn('video_thumbnail', response.data.get('errors'))
