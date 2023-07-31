from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel_factory import ChannelFactory

from apps.channel.models import Channel

from apps.channel.serializers import ChannelDetailsSerializer


class TestChannelDetailsById(APITestCase):
    def setUp(self):
        self.test_channel: Channel = ChannelFactory.create()
        self.url = reverse('channel_details_by_id', kwargs={'pk': self.test_channel.pk})

    def test_to_return_channel_details_by_id_successfully(self):
        response = self.client.get(self.url)

        serialized_channel = ChannelDetailsSerializer(self.test_channel)

        self.assertDictEqual(response.data, serialized_channel.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_error_response_and_status_code_404_if_the_channel_does_not_exists(self):
        self.test_channel.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)