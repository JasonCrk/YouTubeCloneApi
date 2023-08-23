import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestCreateVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('upload_video')

        video_path = os.path.dirname(__file__) + '/resources/test_video.mp4'
        with open(video_path, 'rb') as file:
            video_content = file.read()

        self.video = SimpleUploadedFile('video.mp4', video_content, content_type='video/mp4')

        thumbnail_content = faker.image(size=(2, 2), hue=[90, 270])
        self.thumbnail = SimpleUploadedFile('thumbnail.png', thumbnail_content, content_type='image/png')

    def test_success_response(self):
        """
        Should return a success response if the video has been created
        """
        response = self.client.post(
            self.url,
            {
                'video': self.video,
                'thumbnail': self.thumbnail,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video has been uploaded'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_video_has_been_created(self):
        """
        Should verify if the video has been created successfully
        """
        self.client.post(
            self.url,
            {
                'video': self.video,
                'thumbnail': self.thumbnail,
                'title': faker.pystr(max_chars=45),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        channel_video = Video.objects.filter(channel=self.user.current_channel)

        self.assertEqual(channel_video.count(), 1)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.post(
            self.url,
            {
                'video': faker.pystr(),
                'thumbnail': faker.pystr(),
                'title': faker.pystr(min_chars=46, max_chars=47),
                'description': faker.paragraph()
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('video', response.data.get('errors'))
        self.assertIn('thumbnail', response.data.get('errors'))
        self.assertIn('title', response.data.get('errors'))
