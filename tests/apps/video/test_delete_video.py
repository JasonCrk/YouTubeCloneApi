from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.video_factory import VideoFactory
from tests.factories.channel_factory import ChannelFactory

from apps.video.models import Video
from apps.channel.models import Channel


class TestDeleteVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url = reverse('delete_video', kwargs={'video_id': self.test_video.pk})

    def test_to_return_success_response_if_video_deletion_has_been_successful(self):
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The video has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_video_deletion_has_been_successful(self):
        self.client.delete(self.url)

        video_exists = Video.objects.filter(id=self.test_video.pk).exists()

        self.assertFalse(video_exists)

    def test_to_return_error_response_if_the_video_does_not_exists(self):
        url = reverse('delete_video', kwargs={'video_id': 1000})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_if_the_user_wants_to_delete_a_video_that_is_not_their_own(self):
        other_channel: Channel = ChannelFactory.create(user=self.user)

        not_own_video: Video = VideoFactory.create(channel=other_channel)

        url = reverse('delete_video', kwargs={'video_id': not_own_video.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'You are not the owner of the video'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
