from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel

from apps.channel.serializers import ChannelDetailsSerializer


class TestChannelDetailsById(APITestCase):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()
        self.url = reverse('channel_details_by_id', kwargs={'channel_id': self.channel.pk})

    def test_returns_the_serialized_channel(self):
        """
        Should return the serialized channel and a 200 status code
        """
        response = self.client.get(self.url)

        serialized_channel = ChannelDetailsSerializer(self.channel)

        self.assertDictEqual(response.data, serialized_channel.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_channel_does_not_exist(self):
        """
        Should return an error message and a 404 status code if the channel does not exist
        """
        self.channel.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)