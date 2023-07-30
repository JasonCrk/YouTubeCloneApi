from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.comment_factory import CommentFactory

from apps.comment.models import Comment

from apps.comment.serializers import ListCommentSerializer


class TestCommentsOfComment(APITestCase):
    def setUp(self):
        self.test_parent_comment: Comment = CommentFactory.create()
        self.test_comment_of_comment: Comment = CommentFactory.create(comment=self.test_parent_comment)

        self.url = reverse('comments_of_comment', kwargs={'comment_id': self.test_parent_comment.pk})

    def test_to_return_comments_of_comment_successfully(self):
        response = self.client.get(self.url)

        parent_comment_serialized = ListCommentSerializer(self.test_comment_of_comment)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(
            response.data.get('data')[0],
            parent_comment_serialized.data
        )

    def test_to_return_error_response_if_the_comment_does_not_exists(self):
        self.test_parent_comment.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
