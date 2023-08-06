from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel_factory import ChannelFactory
from tests.factories.link_factory import LinkFactory

from apps.channel.models import Channel
from apps.link.models import Link

from apps.link.serializers import LinkListSerializer


class TestGetChannelLinks(APITestCase):
    def setUp(self):
        self.test_channel: Channel = ChannelFactory.create()
        self.url = reverse('get_channel_links', kwargs={'channel_id': self.test_channel.pk})

    def test_to_return_3_links_from_a_channel(self):
        LinkFactory.create_batch(3, channel=self.test_channel)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data.get('data')), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_serialized_channel_links(self):
        LinkFactory.create_batch(3, channel=self.test_channel)

        response = self.client.get(self.url)

        serialized_first_channel_link = LinkListSerializer(response.data.get('data')[0])

        self.assertEqual(
            response.data.get('data')[0],
            serialized_first_channel_link.data
        )

    def test_to_return_channel_links_sorted_by_position_in_descending_order(self):
        LinkFactory.create_batch(3, channel=self.test_channel)

        response = self.client.get(self.url)

        for index, link in enumerate(response.data.get('data')):
            self.assertEqual(dict(link).get('position'), index)

    def test_to_return_error_response_and_status_code_404_if_the_channel_does_not_exists(self):
        self.test_channel.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
