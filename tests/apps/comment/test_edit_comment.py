from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.comment import CommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestEditComment(TestSetup):
    def setUp(self):
        super().setUp()

        test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.test_comment: Comment = CommentFactory.create(
            channel=self.user.current_channel,
            video=test_video
        )

        self.url = reverse('edit_comment', kwargs={'comment_id': self.test_comment.pk})

    def test_to_return_success_response_if_the_comment_edition_has_been_successful(self):
        response = self.client.put(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_comment_content_has_been_updated_correctly(self):
        new_comment_content = faker.paragraph()

        self.client.put(
            self.url,
            {
                'content': new_comment_content
            },
            format='json'
        )

        comment_updated = Comment.objects.get(id=self.test_comment.pk)

        self.assertEqual(comment_updated.content, new_comment_content)

    def test_to_return_error_response_if_the_comment_does_not_exists(self):
        self.test_comment.delete()

        response = self.client.put(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_if_the_comment_content_is_the_same_as_the_one_in_the_database(self):
        response = self.client.put(
            self.url,
            {
                'content': self.test_comment.content
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment content has not been modified'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_comment_content_is_blank(self):
        response = self.client.put(
            self.url,
            {
                'content': ''
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('content'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
