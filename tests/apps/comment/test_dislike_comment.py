from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.comment import CommentFactory, DislikeCommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment, LikedComment
from apps.video.models import Video


class TestDislikeComment(TestSetup):
    def setUp(self):
        super().setUp()

        test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.test_comment: Comment = CommentFactory.create(
            channel=self.user.current_channel,
            video=test_video
        )

        self.url = reverse('dislike_comment')

    def test_to_return_success_response_if_the_dislike_to_the_comment_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'comment_id': self.test_comment.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Dislike comment added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_dislike_to_the_comment_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'comment_id': self.test_comment.pk
            },
            format='json'
        )

        dislike_comment_exists = LikedComment.objects.filter(
            channel=self.user.current_channel,
            comment=self.test_comment,
            liked=False
        ).exists()

        self.assertTrue(dislike_comment_exists)

    def test_to_return_success_response_if_the_dislike_has_been_successful_deleted(self):
        DislikeCommentFactory.create(
            channel=self.user.current_channel,
            comment=self.test_comment
        )

        response = self.client.post(
            self.url,
            {
                'comment_id': self.test_comment.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Dislike comment removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_dislike_has_been_successful_deleted(self):
        DislikeCommentFactory.create(
            channel=self.user.current_channel,
            comment=self.test_comment
        )

        self.client.post(
            self.url,
            {
                'comment_id': self.test_comment.pk
            },
            format='json'
        )

        dislike_comment_exists = LikedComment.objects.filter(
            channel=self.user.current_channel,
            comment=self.test_comment
        ).exists()

        self.assertFalse(dislike_comment_exists)

    def test_to_return_error_response_if_the_comment_does_not_exists(self):
        non_exists_comment_id = self.test_comment.id

        self.test_comment.delete()

        response = self.client.post(
            self.url,
            {
                'comment_id': non_exists_comment_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_if_the_comment_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'comment_id': 'a'
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
