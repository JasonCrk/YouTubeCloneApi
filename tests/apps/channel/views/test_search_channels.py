from django.urls import reverse
from django.db.models import Q

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel import ChannelFactory, ChannelSubscriptionFactory
from tests.factories.video import VideoFactory, VideoViewFactory
from tests.factories.user_account import UserFactory

from apps.channel.models import Channel
from apps.user.models import UserAccount

from youtube_clone.enums import SortByEnum


class TestSearchChannels(APITestCase):
    def setUp(self):
        self.SEARCH_QUERY = 'test'

        user: UserAccount = UserFactory.create(username=self.SEARCH_QUERY)

        self.url = reverse('search_channels')

        self.first_channel_created: Channel = user.current_channel

        self.channel_with_subscribers: Channel = ChannelFactory.create(
            user=user,
            name=f'{self.SEARCH_QUERY} channel'
        )
        ChannelSubscriptionFactory.create(
            subscriber=self.first_channel_created,
            subscribing=self.channel_with_subscribers
        )

        self.channel_with_views: Channel = ChannelFactory.create(
            user=user,
            name=f'{self.SEARCH_QUERY} channel'
        )

        video = VideoFactory.create(channel=self.channel_with_views)
        VideoViewFactory.create(
            channel=self.first_channel_created,
            video=video
        )

    def test_list_of_channels(self):
        """
        Should return a list of channel that are equal to
        or contain the value of SEARCH_QUERY
        """
        response = self.client.get(self.url, {'search_query': self.SEARCH_QUERY})

        response_data = list(map(lambda data: dict(data), response.data.get('data')))

        self.assertIn(
            self.first_channel_created.name,
            response_data[0].get('name')
        )
        self.assertIn(
            self.channel_with_subscribers.name,
            response_data[1].get('name')
        )
        self.assertIn(
            self.channel_with_views.name,
            response_data[2].get('name')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_number_of_channels(self):
        """
        Should verify if the number of channels that are equal to
        or contain the value of SEARCH_QUERY
        """
        response = self.client.get(self.url, {'search_query': self.SEARCH_QUERY})

        filtered_channels = Channel.objects.filter(
            Q(name=self.SEARCH_QUERY) | Q(name__icontains=self.SEARCH_QUERY)
        )

        self.assertEqual(
            len(response.data.get('data')),
            filtered_channels.count()
        )

    def test_search_query_is_required(self):
        """
        Should return an error response if the search query param is required
        """
        response = self.client.get(self.url, {'search_query': ''})

        self.assertDictEqual(response.data, {'message': 'Search query is required'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sorted_by_UPLOAD_DATE(self):
        """
        Should return a list of channels ordered by publication date
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SortByEnum.UPLOAD_DATE.value
            }
        )

        first_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_channel.get('id'),
            self.first_channel_created.pk,
        )

    def test_sorted_by_VIEW_COUNT(self):
        """
        Should return a list of channels sorted by view count
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SortByEnum.VIEW_COUNT.value
            }
        )

        first_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_channel.get('id'),
            self.channel_with_views.pk
        )

    def test_sorted_by_RATING(self):
        """
        Should return a list of channels sorted by rating
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SortByEnum.RATING.value
            }
        )

        first_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_channel.get('id'),
            self.channel_with_subscribers.pk
        )
