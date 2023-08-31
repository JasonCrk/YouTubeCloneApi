from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.video import DislikeVideoFactory, VideoFactory, VideoViewFactory, LikeVideoFactory

from apps.video.models import Video

from youtube_clone.enums import SearchSortOptions, SearchUploadDate


class TestSearchVideos(APITestCase):
    def setUp(self):
        self.SEARCH_QUERY = 'test'

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

    def test_return_success_status_code(self):
        """
        Should return a success status code if the search has been successfully
        """
        response = self.client.get(self.url,{'search_query': self.SEARCH_QUERY})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_searched_videos(self):
        f"""
        Should return searched videos that have the word "{self.SEARCH_QUERY}" in their title
        """
        first_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        second_expected_video: Video = VideoFactory.create(title=f'{self.SEARCH_QUERY} video')
        no_expected_video: Video = VideoFactory.create()

        response = self.client.get(self.url, {'search_query': self.SEARCH_QUERY})

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertNotIn(no_expected_video.pk, searched_videos_ids)

        self.assertIn(first_expected_video.pk, searched_videos_ids)
        self.assertIn(second_expected_video.pk, searched_videos_ids)

    def test_sorted_by_UPLOAD_DATE(self):
        """
        Should verify that the searched videos are sorted by upload date
        """
        videos = VideoFactory.create_batch(3)

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SearchSortOptions.UPLOAD_DATE.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        for i, video_id in searched_videos_ids:
            self.assertEqual(videos[i], video_id)

    def test_sorted_by_VIEW_COUNT(self):
        """
        Should verify that the searched videos are sorted by view count
        """
        first_video_with_views: Video = VideoFactory(title=f'{self.SEARCH_QUERY} title')
        VideoViewFactory.create(video=first_video_with_views, count=3)
        VideoViewFactory.create(video=first_video_with_views, count=2)

        second_video_with_views = VideoFactory(title=f'{self.SEARCH_QUERY} title')
        VideoViewFactory.create(video=second_video_with_views, count=1)

        video_without_views = VideoFactory(title=self.SEARCH_QUERY)

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY, 
                'sort_by': SearchSortOptions.VIEW_COUNT.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertEqual(searched_videos_ids[0], first_video_with_views.pk)
        self.assertEqual(searched_videos_ids[1], second_video_with_views.pk)
        self.assertEqual(searched_videos_ids[2], video_without_views.pk)

    def test_sorted_by_RATING(self):
        """
        Should verify that the searched videos are sorted by RATING ()
        """
        first_video_with_most_likes: Video = VideoFactory(title=self.SEARCH_QUERY)
        LikeVideoFactory.create(video=first_video_with_most_likes)
        LikeVideoFactory.create(video=first_video_with_most_likes)

        second_video_with_most_likes: Video = VideoFactory(title=self.SEARCH_QUERY)
        LikeVideoFactory.create(video=second_video_with_most_likes)

        video_without_likes: Video = VideoFactory(title=self.SEARCH_QUERY)

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SearchSortOptions.RATING.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertEqual(searched_videos_ids[0], first_video_with_most_likes.pk)
        self.assertEqual(searched_videos_ids[1], second_video_with_most_likes.pk)
        self.assertEqual(searched_videos_ids[2], video_without_likes.pk)

    def test_sorted_by_RATING_ignored_dislikes(self):
        """
        Should return the videos sorted by RATING ignoring the dislikes
        """
        video_with_most_dislikes: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        DislikeVideoFactory.create(video=video_with_most_dislikes)

        video_with_most_likes: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        LikeVideoFactory.create(video=video_with_most_likes)

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'sort_by': SearchSortOptions.RATING.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertEqual(searched_videos_ids[0], video_with_most_likes.pk)
        self.assertEqual(searched_videos_ids[1], video_with_most_dislikes.pk)

    def test_search_by_LAST_HOUR_upload_date(self):
        """
        Should verify that the searched videos are filtered by LAST HOUR upload date
        """
        today = timezone.now()
        different_time = today.replace(hour=today.hour - 1 if today.hour != 0 else today.hour + 1)

        expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        not_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)

        not_expected_video.publication_date = different_time
        not_expected_video.save()

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'upload_date': SearchUploadDate.LAST_HOUR.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(expected_video.pk, searched_videos_ids)
        self.assertNotIn(not_expected_video.pk, searched_videos_ids)

    def test_search_by_TODAY_upload_date(self):
        """
        Should verify that the searched videos are filtered by TODAY upload date
        """
        today = timezone.now()
        different_day = today.replace(day=today.day - 1)

        expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        not_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)

        not_expected_video.publication_date = different_day
        not_expected_video.save()

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'upload_date': SearchUploadDate.TODAY.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(expected_video.pk, searched_videos_ids)
        self.assertNotIn(not_expected_video.pk, searched_videos_ids)

    def test_search_by_THIS_WEEK_upload_date(self):
        """
        Should verify that the searched videos are filtered by THIS WEEK upload date
        """
        today = timezone.now()
        different_week = today.replace(day=today.day - 8)

        expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        not_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)

        not_expected_video.publication_date = different_week
        not_expected_video.save()

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'upload_date': SearchUploadDate.THIS_WEEK.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(expected_video.pk, searched_videos_ids)
        self.assertNotIn(not_expected_video.pk, searched_videos_ids)

    def test_search_by_THIS_MONTH_upload_date(self):
        """
        Should verify that the searched videos are filtered by THIS MONTH upload date
        """
        today = timezone.now()
        different_month = today.replace(month=today.month - 1)

        expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        not_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)

        not_expected_video.publication_date = different_month
        not_expected_video.save()

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'upload_date': SearchUploadDate.THIS_MONTH.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(expected_video.pk, searched_videos_ids)
        self.assertNotIn(not_expected_video.pk, searched_videos_ids)

    def test_search_by_THIS_YEAR_upload_date(self):
        """
        Should verify that the searched videos are filtered by THIS YEAR upload date
        """
        today = timezone.now()
        different_year = today.replace(year=today.year - 1)

        expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)
        not_expected_video: Video = VideoFactory.create(title=self.SEARCH_QUERY)

        not_expected_video.publication_date = different_year
        not_expected_video.save()

        response = self.client.get(
            self.url,
            {
                'search_query': self.SEARCH_QUERY,
                'upload_date': SearchUploadDate.THIS_YEAR.value
            }
        )

        searched_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(expected_video.pk, searched_videos_ids)
        self.assertNotIn(not_expected_video.pk, searched_videos_ids)
