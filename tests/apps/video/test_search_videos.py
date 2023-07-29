from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.user_account_factory import UserFactory
from tests.factories.video_factory import VideoFactory
from tests.factories.video_view_factory import VideoViewFactory
from tests.factories.liked_video_factory import LikeVideoFactory

from apps.user.models import UserAccount

from youtube_clone.enums import SortByEnum


class TestSearchVideos(APITestCase):
    def setUp(self):
        self.user: UserAccount = UserFactory.create()

        self.url = reverse('search_videos')

        self.video_created_today = VideoFactory(
            title='test',
            channel=self.user.current_channel
        )

        self.video_with_likes = VideoFactory(title='test title', channel=self.user.current_channel)
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video_with_likes
        )

        self.video_with_views = VideoFactory(title='test title', channel=self.user.current_channel)
        VideoViewFactory.create(
            channel=self.user.current_channel,
            video=self.video_with_views
        )

        self.last_video_created = VideoFactory(
            title='test',
            channel=self.user.current_channel
        )


    def test_to_return_error_response_if_dont_send_the_search_query(self):
        response = self.client.get(self.url, {'search_query': ''})

        self.assertDictEqual(response.data, {'message': 'Search query is required'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_videos_with_title_equal_or_contains_to_test(self):
        response = self.client.get(self.url, {'search_query': 'test'})

        self.assertIn(
            self.video_created_today.title,
            dict(response.data.get('data')[0])['title']
        )
        self.assertIn(
            self.last_video_created.title,
            dict(response.data.get('data')[1])['title']
        )
        self.assertIn(
            dict(response.data.get('data')[2])['title'],
            self.video_with_likes.title
        )
        self.assertIn(
            dict(response.data.get('data')[3])['title'],
            self.video_with_views.title
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_it_returns_two_videos_with_title_equal_or_contains_to_test(self):
        response = self.client.get(self.url, {'search_query': 'test'})

        self.assertEqual(len(response.data.get('data')), 4)

    def test_to_return_videos_sorted_by_UPLOAD_DATE(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.UPLOAD_DATE.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_created_today.pk
        )

    def test_to_return_videos_sorted_by_VIEW_COUNT(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.VIEW_COUNT.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_with_views.pk
        )

    def test_to_return_videos_sorted_by_RATING(self):
        response = self.client.get(
            self.url,
            {
                'search_query': 'test',
                'sort_by': SortByEnum.RATING.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_with_likes.pk
        )
