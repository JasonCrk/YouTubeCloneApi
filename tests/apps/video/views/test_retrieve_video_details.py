from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.video import VideoFactory

from apps.video.models import Video

from apps.video.serializers import VideoDetailsSerializer

from faker import Faker

faker = Faker()


class TestRetrieveVideoDetails(APITestCase):
    def setUp(self):
        self.video: Video = VideoFactory.create()

        self.url = reverse('video_details', kwargs={'video_id': self.video.pk})

    def test_return_serialized_video(self):
        """
        Should return a serialized video
        """
        response = self.client.get(self.url)

        serialized_video = VideoDetailsSerializer(
            self.video,
            context={'request': response.wsgi_request}
        )

        self.assertDictEqual(response.data, serialized_video.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
