from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.comment import CommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from apps.comment.serializers import ListCommentSerializer


class TestVideoComments(APITestCase):
    def setUp(self):
        self.test_video: Video = VideoFactory.create()
        self.test_video_comment: Comment = CommentFactory.create(video=self.test_video)

        self.url = reverse('video_comments', kwargs={'video_id': self.test_video.pk})

    def test_to_return_comments_on_video_successful(self):
        response = self.client.get(self.url)

        test_video_serialized = ListCommentSerializer(self.test_video_comment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data.get('data')[0],
            test_video_serialized.data
        )

    def test_to_return_error_response_if_video_does_not_exists(self):
        self.test_video.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
