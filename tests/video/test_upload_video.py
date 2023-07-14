import os

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from tests.test_setup import TestSetup

from apps.video.models import Video
from apps.channel.models import Channel
from apps.user.models import UserAccount


class TestCreateVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('upload_video')

        self.channel_id = Channel.objects.get(user=self.user).pk

        test_video_path = os.path.dirname(__file__) + '/resources/test_video.mp4'
        with open(test_video_path, 'rb') as file:
            video_content = file.read()

        self.test_video = SimpleUploadedFile('test_video.mp4', video_content, content_type='video/mp4')

        test_thumbnail_path = os.path.dirname(__file__) + '/resources/test_thumbnail.webp'
        with open(test_thumbnail_path, 'rb') as file:
            thumbnail_content = file.read()

        self.test_thumbnail = SimpleUploadedFile('test_thumbnail.webp', thumbnail_content, content_type='image/*')

    def test_to_return_success_response_if_the_video_creation_is_successful(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        self.assertDictEqual(response.data, {'message': 'The video has been uploaded successfully'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_error_response_if_the_channel_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL='test_id'
        )

        self.assertDictEqual(response.data, {'message': 'The channel ID is not a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_channel_does_not_exist(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(10)
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_check_if_the_video_has_been_created_correctly(self):
        self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        channel_video_count = Video.objects.filter(channel__pk=self.channel_id).count()

        self.assertEqual(channel_video_count, 1)

    def test_to_return_error_response_if_the_user_wants_to_use_a_channel_that_he_does_not_own(self):
        from faker import Faker
        
        faker = Faker()

        test_user = UserAccount.objects.create_user(
            email=faker.email(),
            username='TestMan123412',
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password='TestPassword'
        )

        channel = Channel.objects.get(user=test_user)

        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(channel.id)
        )

        self.assertDictEqual(response.data, {'message': 'You are not the owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_if_the_video_title_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': '',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        self.assertNotEqual(response.data.get('errors').get('title'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_title_exceeds_45_characters(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': 'video title video title video title video title video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        self.assertNotEqual(response.data.get('errors').get('title'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'thumbnail': self.test_thumbnail,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        self.assertNotEqual(response.data.get('errors').get('video'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_thumbnail_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'title': 'video title',
                'description': 'video description'
            },
            format='multipart',
            HTTP_X_CHANNEL=str(self.channel_id)
        )

        self.assertNotEqual(response.data.get('errors').get('thumbnail'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)