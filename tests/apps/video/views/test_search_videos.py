from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.video import VideoFactory, VideoViewFactory, LikeVideoFactory

from youtube_clone.enums import SortByEnum


class TestSearchVideos(APITestCase):
    def setUp(self):
        self.SEARCH_QUERY = 'test'

        self.video_created_today = VideoFactory(title=self.SEARCH_QUERY)

        self.video_with_likes = VideoFactory(title=f'{self.SEARCH_QUERY} title')
        LikeVideoFactory.create(video=self.video_with_likes)

        self.video_with_views = VideoFactory(title=f'{self.SEARCH_QUERY} title')
        VideoViewFactory.create(video=self.video_with_views)

        self.last_video_created = VideoFactory(title=self.SEARCH_QUERY)

        self.url = reverse('search_videos')

    def test_search_query_is_required(self):
        """
        Should return an error response and a 400 status code if the search query is required
        """
        response = self.client.get(
            self.url,
            {
                'search_query': ''
            }
        )

        self.assertDictEqual(response.data, {'message': 'Search query is required'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_searched_videos(self):
        f"""
        Should return searched videos that have the word "{self.SEARCH_QUERY}" in their title
        """
        response = self.client.get(self.url, {'search_query': self.SEARCH_QUERY})

        searched_videos = list(map(lambda video: dict(video), response.data.get('data')))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.video_created_today.title,
            searched_videos[0]['title']
        )
        self.assertIn(
            self.last_video_created.title,
            searched_videos[1]['title']
        )
        self.assertIn(
            self.video_with_likes.title,
            searched_videos[2]['title']
        )
        self.assertIn(
            self.video_with_views.title,
            searched_videos[3]['title']
        )

    def test_number_of_videos_returned(self):
        """
        Should verify if the number of videos returned are 4
        """
        response = self.client.get(self.url, {'search_query': self.SEARCH_QUERY})

        self.assertEqual(len(response.data.get('data')), 4)

    def test_sorted_by_UPLOAD_DATE(self):
        """
        Should verify that the searched videos are sorted by upload date
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SortByEnum.UPLOAD_DATE.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_created_today.pk
        )

    def test_sorted_by_VIEW_COUNT(self):
        """
        Should verify that the searched videos are sorted by view count
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY, 
                'sort_by': SortByEnum.VIEW_COUNT.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_with_views.pk
        )

    def test_sorted_by_RATING(self):
        """
        Should verify that the searched videos are sorted by rating
        """
        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SortByEnum.RATING.value
            }
        )

        first_response_video = dict(response.data.get('data')[0])

        self.assertEqual(
            first_response_video['id'],
            self.video_with_likes.pk
        )
