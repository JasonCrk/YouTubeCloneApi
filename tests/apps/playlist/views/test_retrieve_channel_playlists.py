from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory
from tests.factories.channel import ChannelFactory

from apps.playlist.models import Playlist
from apps.channel.models import Channel

from apps.playlist.serializers import PlaylistListSerializer

from apps.playlist.choices import Visibility


class TestRetrieveChannelPlaylists(APITestCaseWithAuth):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()

        self.url_name = 'channel_playlists'
        self.url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

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

        retrieved_channel_playlists = [dict(playlist).get('id') for playlist in response.data.get('data')]

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
            dict(response.data.get('data')[0]),
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

    def test_return_all_the_channel_playlists_that_is_authenticated(self):
        """
        Should return all the playlists of the channel that is authenticated
        """
        super().setUp()

        channel_private_playlist: Playlist = PlaylistFactory.create(
            channel=self.user.current_channel,
            visibility=Visibility.PRIVATE
        )

        channel_private_playlist.video_thumbnail = PlaylistVideoFactory.create(playlist=channel_private_playlist)
        channel_private_playlist.save()

        channel_public_playlist: Playlist = PlaylistFactory.create(
            channel=self.user.current_channel,
            visibility=Visibility.PUBLIC,
        )

        channel_public_playlist.video_thumbnail = PlaylistVideoFactory.create(playlist=channel_public_playlist)
        channel_public_playlist.save()

        channel_playlist_without_video: Playlist = PlaylistFactory.create(channel=self.user.current_channel)

        url = reverse(self.url_name, kwargs={'channel_id': self.user.current_channel.pk})

        response = self.client.get(url)

        retrieved_channel_playlists = [dict(playlist).get('id') for playlist in response.data.get('data')]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn(channel_private_playlist.pk, retrieved_channel_playlists)
        self.assertIn(channel_public_playlist.pk, retrieved_channel_playlists)
        self.assertNotIn(channel_playlist_without_video.pk, retrieved_channel_playlists)
