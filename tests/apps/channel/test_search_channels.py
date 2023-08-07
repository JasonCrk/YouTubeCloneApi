from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.user_account import UserFactory
from tests.factories.channel import ChannelFactory, ChannelSubscriptionFactory
from tests.factories.video import VideoFactory, VideoViewFactory

from apps.channel.models import Channel
from apps.user.models import UserAccount

from youtube_clone.enums import SortByEnum


class TestSearchChannels(APITestCase):
    def setUp(self):
        user: UserAccount = UserFactory.create(username='test')

        self.url = reverse('search_channels')

        self.first_channel_created: Channel = user.current_channel

        self.channel_with_subscribers: Channel = ChannelFactory.create(
            user=user,
            name='test channel'
        )
        ChannelSubscriptionFactory.create(
            subscriber=self.first_channel_created,
            subscribing=self.channel_with_subscribers
        )

        self.channel_with_views: Channel = ChannelFactory.create(
            user=user,
            name='test channel'
        )
        test_video = VideoFactory.create(channel=self.channel_with_views)
        VideoViewFactory.create(
            channel=self.channel_with_views,
            video=test_video
        )

    def test_to_return_error_response_if_the_search_query_is_null(self):
        response = self.client.get(self.url, {'search_query': ''})

        self.assertDictEqual(response.data, {'message': 'Search query is required'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_two_channels_with_name_equal_or_contains_to_test(self):
        response = self.client.get(self.url, {'search_query': 'test'})

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

    def test_to_check_if_it_return_three_channels_with_name_equal_or_contains_to_tes(self):
        response = self.client.get(self.url, {'search_query': 'test'})

        self.assertEqual(len(response.data.get('data')), 3)

    def test_to_return_channels_sorted_by_UPLOAD_DATE(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.UPLOAD_DATE.value
            }
        )

        first_response_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_channel.get('id'),
            self.first_channel_created.pk,
        )

    def test_to_return_channels_sorted_by_VIEW_COUNT(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.VIEW_COUNT.value
            }
        )

        first_response_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_channel.get('id'),
            self.channel_with_views.pk
        )

    def test_to_return_channels_sorted_by_RATING(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.RATING.value
            }
        )

        first_response_channel = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_channel.get('id'),
            self.channel_with_subscribers.pk
        )
