from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel import ChannelFactory
from tests.factories.link import LinkFactory

from apps.link.models import Link
from apps.channel.models import Channel

from apps.link.serializers import LinkListSerializer


class TestRetrieveChannelLinks(APITestCase):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()
        self.url = reverse('get_channel_links', kwargs={'channel_id': self.channel.pk})

    def test_amount_of_channel_links(self):
        """
        Should verify that the list of channel links contains 3 links
        """
        NUMBER_OF_LINKS = 3

        LinkFactory.create_batch(NUMBER_OF_LINKS, channel=self.channel)

        response = self.client.get(self.url)

        self.assertEqual(len(response.data.get('data')), NUMBER_OF_LINKS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_serialized_channel_link_list(self):
        """
        Should verify if the channel link list is serialized
        """
        links: list[Link] = LinkFactory.create_batch(3, channel=self.channel)

        response = self.client.get(self.url)

        serialized_channel_links = LinkListSerializer(links, many=True)

        self.assertEqual(response.data.get('data'), serialized_channel_links.data)

    def test_links_sorted_by_position_in_descending_order(self):
        """
        Should verify if the channel link list is sorted by position in descending order
        """
        LinkFactory.create_batch(3, channel=self.channel)

        response = self.client.get(self.url)

        for position, link in enumerate(response.data.get('data')):
            self.assertEqual(dict(link).get('position'), position)

    def test_channel_does_not_exists(self):
        """
        Should return an error response and a 404 status code if the channel does not exist
        """
        self.channel.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
