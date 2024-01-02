from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.video.models import Video
from apps.video.serializers import VideoListSerializer

from tests.factories.video import VideoFactory, VideoViewFactory, LikeVideoFactory
from tests.factories.comment import CommentFactory

class TestRetrieveTrendingVideos(APITestCase):
    def setUp(self):
        self.url_name = 'trending_videos'
        self.url = reverse(self.url_name)

        self.second_top_trending_video: Video = VideoFactory.create()
        LikeVideoFactory.create_batch(2, video=self.second_top_trending_video)
        VideoViewFactory.create(video=self.second_top_trending_video, count=10)
        CommentFactory.create(video=self.second_top_trending_video)

        self.video: Video = VideoFactory.create()
        LikeVideoFactory.create(video=self.video)
        VideoViewFactory.create(video=self.video, count=1)

        self.top_trending_video: Video = VideoFactory.create()
        LikeVideoFactory.create_batch(3, video=self.top_trending_video)
        VideoViewFactory.create(video=self.top_trending_video, count=15)
        CommentFactory.create_batch(3, video=self.top_trending_video)

    def test_should_return_a_list_of_serialized_videos(self):
        response = self.client.get(self.url)

        serialized_top_trending_video = VideoListSerializer(self.top_trending_video)

        self.assertIn(serialized_top_trending_video.data, response.data.get('data'))

    def test_should_return_OK_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_should_return_a_list_of_videos_sorted_by_trend(self):
        response = self.client.get(self.url)

        print(response.data.get('data'))

        self.assertEqual(response.data.get('data')[0].get('id'), self.top_trending_video.pk)
        self.assertEqual(response.data.get('data')[1].get('id'), self.second_top_trending_video.pk)
        self.assertEqual(response.data.get('data')[2].get('id'), self.video.pk)
