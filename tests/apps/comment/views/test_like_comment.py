from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory, DislikeCommentFactory, LikeCommentFactory

from apps.comment.models import Comment, LikedComment


class TestLikeComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.comment: Comment = CommentFactory.create(channel=self.user.current_channel)

        self.url_name = 'like_comment'

    def test_success_response_if_like_comment_added(self):
        """
        Should return a success response if the like to the comment has been added
        """
        url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Like comment added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_comment_added(self):
        """
        Should verify if the like to the comment has been added successfully
        """
        url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

        self.client.post(url)

        like_comment = LikedComment.objects.filter(
            channel=self.user.current_channel,
            comment=self.comment
        )

        self.assertTrue(like_comment.exists())

    def test_success_response_if_like_comment_removed(self):
        """
        Should return a success response if the like to the comment has been removed
        """
        LikeCommentFactory.create(
            channel=self.user.current_channel,
            comment=self.comment
        )

        url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Like comment removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_like_comment_removed(self):
        """
        Should verify if the like to the comment has been removed successfully
        """
        LikeCommentFactory.create(
            channel=self.user.current_channel,
            comment=self.comment
        )

        url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

        self.client.post(url)

        like_comment = LikedComment.objects.filter(
            channel=self.user.current_channel,
            comment=self.comment
        )

        self.assertFalse(like_comment.exists())

    def test_dislike_comment_to_like_comment(self):
        """
        Should verify that if the comment has our dislike it will convert it to a like
        """
        DislikeCommentFactory.create(
            channel=self.user.current_channel,
            comment=self.comment
        )

        url = reverse(self.url_name, kwargs={'comment_id': self.comment.pk})

        self.client.post(url)

        like_comment = LikedComment.objects.filter(
            channel=self.user.current_channel,
            comment=self.comment,
            liked=True
        )

        self.assertTrue(like_comment.exists())

    def test_comment_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the comment does not exist
        """
        non_exist_comment_id = self.comment.pk

        self.comment.delete()

        non_exist_comment_url = reverse(self.url_name, kwargs={'comment_id': non_exist_comment_id})

        response = self.client.post(non_exist_comment_url)

        self.assertDictEqual(response.data, {'message': 'The comment does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
