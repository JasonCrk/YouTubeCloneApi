from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory
from tests.factories.video import VideoFactory
from tests.factories.channel import ChannelFactory

from apps.comment.models import Comment
from apps.video.models import Video
from apps.channel.models import Channel


class TestDeleteComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.test_comment: Comment = CommentFactory.create(
            channel=self.user.current_channel,
            video=test_video
        )

        self.url = reverse('delete_comment', kwargs={'comment_id': self.test_comment.pk})

    def test_to_return_success_response_if_the_comment_deletion_has_been_successful(self):
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_comment_deletion_has_been_successful(self):
        self.client.delete(self.url)

        comment_exists = Comment.objects.filter(id=self.test_comment.pk).exists()

        self.assertFalse(comment_exists)

    def test_to_return_error_response_if_the_comment_does_not_exists(self):
        self.test_comment.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The comment does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_if_the_user_wants_to_delete_a_comment_that_is_not_their_own(self):
        test_channel: Channel = ChannelFactory.create(user=self.user)

        test_video: Video = VideoFactory.create(channel=test_channel)

        non_own_comment: Comment = CommentFactory.create(channel=test_channel, video=test_video)

        url_delete_non_own_comment = reverse('delete_comment', kwargs={'comment_id': non_own_comment.pk})

        response = self.client.delete(url_delete_non_own_comment)

        self.assertDictEqual(response.data, {'message': 'You do not own this comment'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
