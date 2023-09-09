from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory, LikeVideoFactory, DislikeVideoFactory

from apps.video.models import Video, LikedVideo

from faker import Faker

faker = Faker()


class TestLikeVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url_name = 'like_video'

    def test_success_response(self):
        """
        Should return a success response if the like to video has been added
        """
        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Like video added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_video_added(self):
        """
        Should verify if the like to video has been added successfully
        """
        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        like_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=True
        )

        self.assertTrue(like_video.exists())

    def test_return_success_response_if_like_video_has_been_removed(self):
        """
        Should return a success response if the like to video has been removed
        """
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Like video removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_video_removed(self):
        """
        Should verify if the like to video has been removed successfully
        """
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        like_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=True
        )

        self.assertFalse(like_video.exists())

    def test_dislike_video_to_like_video(self):
        """
        Should verify that if the video has our dislike it will convert it to a like
        """
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        like_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=True
        )

        self.assertTrue(like_video.exists())

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        non_exist_video_id = self.video.pk

        self.video.delete()

        non_exist_video_url = reverse(self.url_name, kwargs={'video_id': non_exist_video_id})

        response = self.client.post(non_exist_video_url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
