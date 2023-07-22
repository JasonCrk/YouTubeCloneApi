import os

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from tests.test_setup import TestSetup

from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestCreateVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('upload_video')

        test_video_path = os.path.dirname(__file__) + '/resources/test_video.mp4'
        with open(test_video_path, 'rb') as file:
            video_content = file.read()

        self.test_video = SimpleUploadedFile('test_video.mp4', video_content, content_type='video/mp4')

        thumbnail_content = faker.image(size=(16, 16), hue=[90, 270])
        self.test_thumbnail = SimpleUploadedFile('test_thumbnail.png', thumbnail_content, content_type='image/png')

    def test_to_return_success_response_if_the_video_creation_is_successful(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video has been uploaded successfully'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_video_has_been_created_correctly(self):
        self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        channel_video_count = Video.objects.filter(channel=self.user.current_channel).count()

        self.assertEqual(channel_video_count, 1)

    def test_to_return_error_response_if_the_video_title_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': '',
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('title'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_title_exceeds_45_characters(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'thumbnail': self.test_thumbnail,
                'title': faker.pystr(min_chars=46, max_chars=47),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('title'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'thumbnail': self.test_thumbnail,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('video'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_thumbnail_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'video': self.test_video,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('thumbnail'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
