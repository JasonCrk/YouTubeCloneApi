from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.video_factory import VideoFactory

from apps.video.models import Video

from apps.video.serializers import VideoDetailsSerializer

from faker import Faker

faker = Faker()


class TestVideoDetails(APITestCase):
    def setUp(self):
        self.test_video: Video = VideoFactory.create()

        self.test_video_serialized = VideoDetailsSerializer(self.test_video).data

        self.url = reverse('video_details', kwargs={'pk': self.test_video.pk})

    def test_to_return_video_details_successful(self):
        response = self.client.get(self.url)

        self.assertDictEqual(response.data, self.test_video_serialized)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_error_response_if_the_video_does_not_exists(self):
        self.test_video.delete()

        response = self.client.get(self.url)

        self.assertIsNotNone(response.data.get('detail'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
