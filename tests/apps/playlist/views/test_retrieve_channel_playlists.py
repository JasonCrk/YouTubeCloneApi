from django.urls import reverse
from django.test import TestCase

from rest_framework import status

from tests.factories.playlist import PlaylistFactory
from tests.factories.channel import ChannelFactory

from apps.playlist.models import Playlist
from apps.channel.models import Channel

from apps.playlist.serializers import PlaylistListSerializer

from apps.playlist.choices import Visibility


class TestRetrieveChannelPlaylists(TestCase):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()
        self.url = reverse('channel_playlists', kwargs={'channel_id': self.channel.pk})

    def test_return_channel_playlists_with_visibility_PUBLIC(self):
        """
        Should return a channel playlists with visibility in PUBLIC
        """
        channel_playlists: list[Playlist] = PlaylistFactory.create_batch(
            2,
            channel=self.channel,
            visibility=Visibility.PUBLIC
        )
        not_own_playlist: Playlist = PlaylistFactory.create(visibility=Visibility.PUBLIC)

        response = self.client.get(self.url)

        retrieved_channel_playlists = list(map(
            lambda playlist: dict(playlist).get('id'),
            response.data.get('data')
        ))

        self.assertNotIn(vars(not_own_playlist).get('id'), retrieved_channel_playlists)

        for channel_playlist in channel_playlists:
            self.assertIn(vars(channel_playlist).get('id'), retrieved_channel_playlists)

    def test_return_serialized_channel_playlists(self):
        """
        Should verify if it returns serialized channel playlists
        """
        channel_playlist = PlaylistFactory.create(
            channel=self.channel,
            visibility=Visibility.PUBLIC
        )

        serialized_channel_playlist = PlaylistListSerializer(channel_playlist)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data.get('data')[0],
            serialized_channel_playlist.data
        )

    def test_channel_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the channel does not exist
        """
        self.channel.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
