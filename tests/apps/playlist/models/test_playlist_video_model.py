from django.test import TestCase

from tests.factories.playlist import PlaylistVideoFactory

from apps.playlist.models import PlaylistVideo


class TestPlaylistVideoModel(TestCase):
    def setUp(self):
        self.playlist_video: PlaylistVideo = PlaylistVideoFactory.create()

    def test_str_of_the_playlist_video_model_is_the_video_name(self):
        """
        Should verify if the __str__() of the playlist video model is the video title
        """
        self.assertEqual(self.playlist_video.__str__(), self.playlist_video.video.title)

    def test_playlist_video_has_been_created(self):
        """
        Should verify if the playlist video has been created
        """
        playlist_video = PlaylistVideo.objects.filter(id=self.playlist_video.pk)
        self.assertTrue(playlist_video.exists())

    def test_increase_in_position_of_a_created_playlist_video(self):
        """
        Should verify that the position of the created playlist video is greater than all the playlist videos that the playlist has
        """
        new_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist_video.playlist)
        self.assertEqual(new_playlist_video.position, self.playlist_video.position + 1)

    def test_rearrangement_of_playlist_video_positions(self):
        """
        Should verify that the playlist videos are organized when a playlist video is deleted
        """
        playlist = self.playlist_video.playlist

        PlaylistVideoFactory.create_batch(2, playlist=playlist)

        self.playlist_video.delete()

        playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)

        for new_position, playlist_video in enumerate(playlist_videos):
            self.assertEqual(playlist_video.position, new_position)
