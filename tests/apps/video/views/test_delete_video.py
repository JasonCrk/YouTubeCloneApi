from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory

from apps.video.models import Video


class TestDeleteVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url_name = 'delete_video'
        self.url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

    def test_success_response(self):
        """
        Should return a success response if the video has been deleted
        """
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The video has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_has_been_deleted(self):
        """
        Should verify if the video has been deleted successfully
        """
        self.client.delete(self.url)

        video = Video.objects.filter(id=self.video.pk)

        self.assertFalse(video.exists())

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_another_channel_wants_to_delete_a_video_is_not_their_own(self):
        """
        Should return an error response and a 401 status code if another channel wants to delete a video is not their own
        """
        not_own_video: Video = VideoFactory.create()

        not_own_video_url = reverse(self.url_name, kwargs={'video_id': not_own_video.pk})

        response = self.client.delete(not_own_video_url)

        self.assertDictEqual(response.data, {'message': 'You are not the owner of the video'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
