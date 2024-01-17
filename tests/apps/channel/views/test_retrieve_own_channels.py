from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel
from apps.channel.serializers import ChannelListSerializer


class TestRetrieveOwnChannels(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url_name = 'retrieve_own_channels'
        self.url = reverse(self.url_name)

    def test_should_return_status_code_OK(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_should_return_a_channel_list(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data.get('data')), 1)

    def test_should_the_list_be_serialized(self):
        response = self.client.get(self.url)

        serialized_current_channel = ChannelListSerializer(self.user.current_channel)

        self.assertDictEqual(
            response.data.get('data')[0],
            serialized_current_channel.data
        )

    def test_should_the_channels_be_from_the_authenticated_user(self):
        not_own_channel = ChannelFactory.create()

        response = self.client.get(self.url)

        channel_ids = [dict(channel).get('id') for channel in response.data.get('data')]

        self.assertIn(self.user.current_channel.id, channel_ids)
        self.assertNotIn(not_own_channel.pk, channel_ids)

    def test_should_be_sorted_by_creation_date(self):
        own_channels: list[Channel] = ChannelFactory.create_batch(2, user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.data.get('data')[0].get('id'), self.user.current_channel.pk)
        self.assertEqual(response.data.get('data')[1].get('id'), own_channels[0].pk)
        self.assertEqual(response.data.get('data')[2].get('id'), own_channels[1].pk)
