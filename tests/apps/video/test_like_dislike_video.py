from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.VideoFactory import VideoFactory
from tests.factories.LikedVideoFactory import LikeVideoFactory, DislikeVideoFactory

from apps.video.models import Video, LikedVideo

from faker import Faker

faker = Faker()


class TestLikeAndDislikeVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('like_dislike_video')

        self.test_video: Video = VideoFactory.create(channel=self.user.current_channel)

    def test_to_return_error_response_if_the_video_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'video_id': faker.pystr(),
                'liked': True
            },
            format='json'
        )

        self.assertNotEqual(response.data.get('errors').get('video_id'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_liked_is_not_a_boolean(self):
        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': 'test'
            },
            format='json'
        )

        self.assertNotEqual(response.data.get('errors').get('liked'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_does_not_exist(self):
        response = self.client.post(
            self.url,
            {
                'video_id': 1000,
                'liked': True
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_success_response_if_the_user_liked_to_video_successfully(self):
        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': True
            },
            format='json'
        )

        self.assertEqual(response.data, {'message': 'Like video'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_user_liked_to_video_successful(self):
        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': True
            },
            format='json'
        )

        like_exists = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.test_video,
            liked=True
        ).exists()

        self.assertTrue(like_exists)

    def test_to_return_success_response_if_the_user_disliked_to_video_successfully(self):
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': False
            },
            format='json'
        )

        self.assertEqual(response.data, {'message': 'Dislike video'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_user_disliked_to_video_successful(self):
        like_video: LikedVideo = LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': False
            },
            format='json'
        )

        dislike_video = LikedVideo.objects.get(id=like_video.pk)

        self.assertFalse(dislike_video.liked)

    def test_to_return_success_response_if_the_user_removes_his_like_from_the_video(self):
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': True
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The like has been removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_user_removes_his_like_from_the_video(self):
        LikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': True
            },
            format='json'
        )

        like_video_exists = LikedVideo.objects.filter(
            channel=self.user.current_channel,
            video=self.test_video
        ).exists()

        self.assertFalse(like_video_exists)

    def test_to_return_success_response_if_the_user_removes_his_dislike_from_the_video(self):
        DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        response = self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': False
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The dislike has been removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_user_removes_his_dislike_from_the_video(self):
        dislike_video: LikedVideo = DislikeVideoFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        self.client.post(
            self.url,
            {
                'video_id': self.test_video.pk,
                'liked': False
            },
            format='json'
        )

        dislike_video_exists = LikedVideo.objects.filter(id=dislike_video.pk).exists()

        self.assertFalse(dislike_video_exists)
