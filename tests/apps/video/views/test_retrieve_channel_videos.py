from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.channel import ChannelFactory

from tests.factories.video import VideoFactory, VideoViewFactory

from apps.video.models import Video
from apps.channel.models import Channel

from apps.video.serializers import VideoListSimpleSerializer

from youtube_clone.enums import VideoSortOptions


class TestRetrieveChannelVideos(APITestCase):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()

        self.url_name = 'channel_videos'
        self.url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

    def test_return_success_status_code(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_channel_videos(self):
        channel_video: Video = VideoFactory.create(channel=self.channel)
        video_of_another_channel: Video = VideoFactory.create()

        response = self.client.get(self.url)

        channel_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertIn(channel_video.pk, channel_videos_ids)
        self.assertNotIn(video_of_another_channel, channel_videos_ids)

    def test_return_serialized_channel_videos(self):
        video = VideoFactory.create(channel=self.channel)

        serialized_video = VideoListSimpleSerializer(video)

        response = self.client.get(self.url)

        first_video_retrieved = dict(response.data.get('data')[0])

        self.assertEqual(first_video_retrieved, serialized_video.data)

    def test_return_channel_videos_sorted_by_MOST_POPULAR(self):
        first_most_popular_video: Video = VideoFactory.create(channel=self.channel)
        VideoViewFactory.create(video=first_most_popular_video, count=3)
        VideoViewFactory.create(video=first_most_popular_video, count=2)

        second_most_popular_video: Video = VideoFactory.create(channel=self.channel)
        VideoViewFactory.create(video=second_most_popular_video, count=1)

        video_without_views: Video = VideoFactory.create(channel=self.channel)

        response = self.client.get(self.url, {'sort_by': VideoSortOptions.MOST_POPULAR.value})

        channel_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        self.assertEqual(channel_videos_ids[0], first_most_popular_video.pk)
        self.assertEqual(channel_videos_ids[1], second_most_popular_video.pk)
        self.assertEqual(channel_videos_ids[2], video_without_views.pk)

    def test_return_channel_videos_sorted_by_OLDEST_UPLOADED(self):
        NUMBER_VIDEOS = 3

        videos: list[Video] = VideoFactory.create_batch(NUMBER_VIDEOS, channel=self.channel)

        response = self.client.get(self.url, {'sort_by': VideoSortOptions.OLDEST_UPLOADED.value})

        channel_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        for i, video in enumerate(videos):
            self.assertEqual(video.pk, channel_videos_ids[NUMBER_VIDEOS - i - 1])

    def test_return_channel_videos_sorted_by_RECENTLY_UPLOADED(self):
        videos: list[Video] = VideoFactory.create_batch(3, channel=self.channel)

        response = self.client.get(self.url, {'sort_by': VideoSortOptions.RECENTLY_UPLOADED.value})

        channel_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        for i, video in enumerate(videos):
            self.assertEqual(video.pk, channel_videos_ids[i])

    def test_return_channel_videos_sorted_by_RECENTLY_UPLOADED_by_default(self):
        videos: list[Video] = VideoFactory.create_batch(3, channel=self.channel)

        response = self.client.get(self.url)

        channel_videos_ids = [dict(video).get('id') for video in response.data.get('data')]

        for i, video in enumerate(videos):
            self.assertEqual(video.pk, channel_videos_ids[i])

    def test_channel_does_not_exist(self):
        self.channel.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
