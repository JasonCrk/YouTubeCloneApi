from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory

from apps.playlist.models import Playlist, PlaylistVideo


class TestRemoveVideoFromPlaylist(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.playlist: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        self.playlist_video_delete: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        self.url_name = 'remove_video_from_playlist'

        self.url = reverse(
            self.url_name,
            kwargs={'playlist_video_id': self.playlist_video_delete.pk}
        )

    def test_should_return_a_success_response(self):
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': f'Removed from {self.playlist.name}'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_that_the_video_has_been_removed_from_the_playlist(self):
        self.client.delete(self.url)

        playlist_video_removed = PlaylistVideo.objects.filter(id=self.playlist_video_delete.pk)

        self.assertFalse(playlist_video_removed.exists())

    def test_verify_that_the_remaining_videos_in_the_playlist_are_rearranged(self):
        AMOUNT_OF_PLAYLIST_VIDEOS = 2

        PlaylistVideoFactory.create_batch(AMOUNT_OF_PLAYLIST_VIDEOS, playlist=self.playlist)

        self.client.delete(self.url)

        playlist_videos = PlaylistVideo.objects.filter(playlist=self.playlist).order_by('position')

        self.assertEqual(playlist_videos.count(), AMOUNT_OF_PLAYLIST_VIDEOS)
        for position, playlist_video in enumerate(playlist_videos):
            self.assertEqual(position, playlist_video.position)

    def test_should_an_error_message_if_the_playlist_video_does_not_exist(self):
        self.playlist_video_delete.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The playlist video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_should_an_error_response_if_another_channel_wants_to_remove_a_video_from_a_playlist_it_does_not_own(self):
        not_own_playlist_video: PlaylistVideo = PlaylistVideoFactory.create()

        url = reverse(self.url_name, kwargs={'playlist_video_id': not_own_playlist_video.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': "You can't remove a video from a playlist that you don't own"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
