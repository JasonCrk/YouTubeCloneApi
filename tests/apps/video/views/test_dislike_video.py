from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory, DislikeVideoFactory, LikeVideoFactory

from apps.video.models import Video, LikedVideo

from faker import Faker

faker = Faker()


class TestDislikeVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url_name = 'dislike_video'

    def test_return_success_response_if_the_dislike_to_video_has_been_added(self):
        """
        Should return a success response if the dislike video has been added
        """
        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Dislike video added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dislike_video_added(self):
        """
        Should verify if the dislike to video has been added successfully
        """
        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        dislike_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=False
        )

        self.assertTrue(dislike_video.exists())

    def test_return_success_response_if_the_dislike_to_video_has_been_removed(self):
        """
        Should return a success response if the dislike to video has been removed
        """
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Dislike video removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dislike_video_removed(self):
        """
        Should verify if the dislike to video has been removed successfully
        """
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        dislike_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=False
        )

        self.assertFalse(dislike_video.exists())

    def test_like_video_to_dislike_video(self):
        """
        Should verify that if the video has our like it will convert it to a dislike
        """
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

        self.client.post(url)

        dislike_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=False
        )

        self.assertTrue(dislike_video.exists())

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
