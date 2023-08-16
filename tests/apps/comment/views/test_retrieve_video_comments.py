from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.comment import CommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from apps.comment.serializers import ListCommentSerializer


class TestRetrieveVideoComments(APITestCase):
    def setUp(self):
        self.video: Video = VideoFactory.create()

        self.url = reverse('video_comments', kwargs={'video_id': self.video.pk})

    def test_video_comment_list(self):
        """
        Should return a video comment list
        """
        video_comments: Comment = CommentFactory.create_batch(2, video=self.video)

        response = self.client.get(self.url)

        video_comments_serialized = ListCommentSerializer(video_comments, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data.get('data'),
            video_comments_serialized.data
        )

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
