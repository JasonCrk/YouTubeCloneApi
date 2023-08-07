from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.video import VideoFactory

from apps.video.models import Video

from apps.video.serializers import VideoDetailsSerializer

from faker import Faker

faker = Faker()


class TestVideoDetails(APITestCase):
    def setUp(self):
        self.test_video: Video = VideoFactory.create()
        self.url = reverse('video_details', kwargs={'pk': self.test_video.pk})

    def test_to_return_video_details_successful(self):
        response = self.client.get(self.url)

        serialized_test_video = VideoDetailsSerializer(self.test_video)

        self.assertDictEqual(response.data, serialized_test_video.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_error_response_and_status_code_404_if_the_video_does_not_exists(self):
        self.test_video.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
