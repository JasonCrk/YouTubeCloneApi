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
        self.playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        self.video: Video = VideoFactory.create()

        self.url_name = 'save_video_to_playlist'
        self.url = reverse(self.url_name, kwargs={'playlist_id': self.playlist.pk})

    def test_success_response(self):
        """
        Should return a success response if the video has been saved to the playlist
        """
        response = self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': f'Added to {self.playlist.name}'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_video_has_been_saved_to_the_playlist(self):
        """
        Should verify if the video has been saved to the playlist successfully
        """
        self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

        playlist_video = PlaylistVideo.objects.filter(
            playlist=self.playlist,
            video=self.video
        )

        self.assertTrue(playlist_video.exists())

    def test_another_channel_wants_to_save_a_video_to_the_playlist_that_he_does_not_own(self):
        """
        Should return an error response if and a 401 status code
        if another channel wants to save a video to the playlist is does not own
        """
        not_own_playlist: Playlist = PlaylistFactory.create()

        not_own_playlist_url = reverse(self.url_name, kwargs={'playlist_id': not_own_playlist.pk})

        response = self.client.post(
            not_own_playlist_url,
            {
                'video_id': self.video.pk
            },
            format=None
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this playlist'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the playlist does not exist
        """
        self.playlist.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        non_exist_video_id = self.video.pk

        self.video.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': non_exist_video_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_the_video_already_in_a_playlist(self):
        """
        Should return an error response and a 404 status code if the video already in a playlist
        """
        PlaylistVideoFactory.create(
            playlist=self.playlist,
            video=self.video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format=None
        )

        self.assertDictEqual(response.data, {'message': 'The video is already in the playlist'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_id_is_not_a_number(self):
        """
        Should return an error response and a 400 status code if the video ID is not a number
        """
        response = self.client.post(
            self.url,
            {
                'video_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
