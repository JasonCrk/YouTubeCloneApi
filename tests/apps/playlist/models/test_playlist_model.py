from django.test import TestCase

from tests.factories.playlist import PlaylistFactory

from apps.playlist.models import Playlist


class TestPlaylistModel(TestCase):
    def setUp(self):
        self.playlist: Playlist = PlaylistFactory.create()

    def test_str_of_the_playlist_model_is_the_playlist_name(self):
        """
        Should verify if the __str__() of the playlist model is the playlist name
        """
        self.assertEqual(self.playlist.__str__(), self.playlist.name)

    def test_playlist_has_been_created(self):
        """
        Should verify if the playlist has been created
        """
        playlist = Playlist.objects.filter(id=self.playlist.pk)
        self.assertTrue(playlist.exists())

    def test_ordering_to_updated_at(self):
        """
        Should verify if retrieve playlists are sorted by updated_at
        """
        second_playlist = PlaylistFactory.create()

        playlists_ids = Playlist.objects.values_list('id', flat=True)

        self.assertEqual(playlists_ids[0], second_playlist.pk)
        self.assertEqual(playlists_ids[1], self.playlist.pk)
