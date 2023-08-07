from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.video import VideoFactory, DislikeVideoFactory

from apps.video.models import Video, LikedVideo

from faker import Faker

faker = Faker()


class TestDislikeVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('dislike_video')

        self.test_video: Video = VideoFactory.create(channel=self.user.current_channel)

    def test_to_return_success_response_if_the_dislike_video_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Dislike video added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_dislike_video_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        dislike_comment_exists = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.test_video,
            liked=False
        ).exists()

        self.assertTrue(dislike_comment_exists)

    def test_to_return_success_response_if_the_dislike_video_has_been_successful_deleted(self):
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Dislike video removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_dislike_video_has_been_successful_deleted(self):
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk
            },
            format='json'
        )

        dislike_comment_exists = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.test_video,
            liked=False
        ).exists()

        self.assertFalse(dislike_comment_exists)

    def test_to_return_error_response_if_the_video_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'video_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_does_not_exists(self):
        non_exists_video_id = self.test_video.pk
        
        self.test_video.delete()

        response = self.client.post(
            self.url,
            {
                'video_id': non_exists_video_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
