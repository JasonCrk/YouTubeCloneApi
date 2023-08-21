from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory

from apps.comment.models import Comment


class TestDeleteComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.comment: Comment = CommentFactory.create(channel=self.user.current_channel)

        self.url_name = 'delete_comment'
        self.url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

    def test_success_response(self):
        """
        Should return a success response if the comment has been deleted
        """
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_has_been_deleted(self):
        """
        Should verify if the comment has been deleted successfully
        """
        self.client.delete(self.url)

        comment = Comment.objects.filter(id=self.comment.pk)

        self.assertFalse(comment.exists())

    def test_comment_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the comment does not exist
        """
        self.comment.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_channel_wants_to_delete_a_comment_that_is_not_their_owh(self):
        """
        Should return an error response and a 401 status code if a channel wants to delete a comment that is not their own
        """
        not_own_comment: Comment = CommentFactory.create()

        not_own_comment_url = reverse(self.url_name, kwargs={'comment_id': not_own_comment.pk})

        response = self.client.delete(not_own_comment_url)

        self.assertDictEqual(response.data, {'message': 'You do not own this comment'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
