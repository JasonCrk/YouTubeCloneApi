from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory
from tests.factories.video import VideoFactory

from apps.playlist.models import Playlist, PlaylistVideo
from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestSaveVideoToPlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.test_playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        self.test_video: Video = VideoFactory.create()

        self.url_name = 'save_video_to_playlist'
        self.url = reverse(self.url_name, kwargs={'playlist_id': self.test_playlist.pk})

    def test_to_return_success_response_if_the_video_has_been_saved_to_the_playlist_successfully(self):
        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': f'Added to {self.test_playlist.name}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_to_check_if_the_video_has_been_saved_to_the_playlist_successfully(self):
        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        playlist_video = PlaylistVideo.objects.filter(
            playlist=self.test_playlist,
            video=self.test_video
        )

        self.assertTrue(playlist_video.exists())

    def test_to_check_if_the_video_position_is_successive(self):
        first_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(
            playlist=self.test_playlist,
            video=self.test_video
        )

        second_test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'video_id': second_test_video.pk
            },
            format='json'
        )

        second_playlist_video: PlaylistVideo = PlaylistVideo.objects.get(
            playlist=self.test_playlist,
            video=second_test_video
        )

        self.assertEqual(second_playlist_video.position, first_playlist_video.position + 1)

    def test_to_return_error_response_and_status_code_401_if_a_channel_wants_to_save_a_video_to_the_playlist_that_he_does_not_own(self):
        not_own_test_playlist: Playlist = PlaylistFactory.create()

        url = reverse(self.url_name, kwargs={'playlist_id': not_own_test_playlist.pk})

        response = self.client.post(
            url,
            {
                'video_id': self.test_video.pk
            },
            format=None
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_and_status_code_404_if_the_playlist_does_not_exists(self):
        self.test_playlist.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_404_if_the_video_does_not_exists(self):
        non_exist_test_video_id = self.test_video.pk

        self.test_video.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': non_exist_test_video_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_400_if_the_video_already_in_a_playlist(self):
        PlaylistVideoFactory.create(
            playlist=self.test_playlist,
            video=self.test_video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format=None
        )

        self.assertDictEqual(response.data, {'message': 'The video is already in the playlist'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_video_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'video_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
