from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory, VideoViewFactory

from apps.video.models import Video, VideoView


class TestAddVisitToVideo(APITestCaseWithAuth):
    def setUp(self):
        self.video: Video = VideoFactory.create()

        self.url = reverse('visit_to_video', kwargs={'video_id': self.video.pk})

    def test_return_no_content_status_code(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_verify_video_view_for_unauthenticated_users_has_been_created(self):
        self.client.post(self.url)

        video_view = VideoView.objects.filter(channel=None, video=self.video)

        self.assertTrue(video_view.exists())

    def test_verify_video_view_of_a_user_has_been_created(self):
        super().setUp()

        self.client.post(self.url)

        video_view = VideoView.objects.filter(
            channel=self.user.current_channel,
            video=self.video
        )

        self.assertTrue(video_view.exists())

    def test_verify_video_views_from_unauthenticated_users_have_increased(self):
        video_view: VideoView = VideoViewFactory.create(channel=None, video=self.video)

        self.client.post(self.url)

        video_view_updated = VideoView.objects.get(channel=None, video=self.video)

        self.assertEqual(video_view_updated.count, video_view.count + 1)

    def test_verify_video_views_from_user_have_increased(self):
        super().setUp()

        video_view: VideoView = VideoViewFactory.create(
            channel=self.user.current_channel,
            video=self.video
        )

        self.client.post(self.url)

        video_view_updated = VideoView.objects.get(
            channel=self.user.current_channel,
            video=self.video
        )

        self.assertEqual(video_view_updated.count, video_view.count + 1)

    def test_video_does_not_exist(self):
        self.video.delete()

        response = self.client.post(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
