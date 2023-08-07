from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestCreateCommentForComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.test_comment: Comment = CommentFactory.create(
            channel=self.user.current_channel,
            video=self.test_video
        )

        self.url = reverse('create_comment_for_comment', kwargs={'comment_id': self.test_comment.pk})

    def test_to_return_success_response_if_the_comment_creation_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment has been created'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_to_check_if_the_comment_creation_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        number_comment_comments = Comment.objects.filter(comment=self.test_comment).count()

        self.assertEqual(number_comment_comments, 1)

    def test_to_return_error_response_if_the_comment_content_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'content': ''
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('content'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_parent_comment_does_not_exists(self):
        self.test_comment.delete()

        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The parent comment does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
