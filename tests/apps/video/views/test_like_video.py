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

        self.url = reverse('like_video')

    def test_success_response(self):
        """
        Should return a success response if the like to video has been added
        """
        response = self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Like video added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_video_added(self):
        """
        Should verify if the like to video has been added successfully
        """
        self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

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

        response = self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

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

        self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

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

        self.client.post(
            self.url,
            {
                'video_id': self.video.pk
            },
            format='json'
        )

        like_video = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.video,
            liked=True
        )

        self.assertTrue(like_video.exists())

    def test_video_id_is_not_a_number(self):
        """
        Should return an error response and a 400 status code if the video ID is not a number
        """
        response = self.client.post(
            self.url,
            {
                'video_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        non_exist_video_id = self.video.pk

        self.video.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': non_exist_video_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
