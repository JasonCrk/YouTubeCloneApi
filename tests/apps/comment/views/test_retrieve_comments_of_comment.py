from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.comment import CommentFactory

from apps.comment.models import Comment

from apps.comment.serializers import CommentListSerializer


class TestRetrieveCommentsOfComment(APITestCase):
    def setUp(self):
        self.parent_comment: Comment = CommentFactory.create()
        self.url = reverse('comments_of_comment', kwargs={'comment_id': self.parent_comment.pk})

    def test_comment_list_of_a_comment(self):
        """
        Should return a comment list of a comment
        """
        comments_of_comment: list[Comment] = CommentFactory.create_batch(2, comment=self.parent_comment)

        response = self.client.get(self.url)

        serialized_comments = CommentListSerializer(comments_of_comment, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            response.data.get('data'),
            serialized_comments.data
        )

    def test_comment_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the comment does not exist
        """
        self.parent_comment.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
