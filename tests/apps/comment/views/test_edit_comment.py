from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory

from apps.comment.models import Comment

from faker import Faker

faker = Faker()


class TestEditComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.comment: Comment = CommentFactory.create(channel=self.user.current_channel)
        self.url = reverse('edit_comment', kwargs={'comment_id': self.comment.pk})

    def test_success_response(self):
        """
        Should return a success response if the comment has been updated
        """
        response = self.client.put(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_comment_content_has_been_updated(self):
        """
        Should verify if the comment content has been updated successfully
        """
        new_comment_content = faker.paragraph()

        self.client.put(
            self.url,
            {
                'content': new_comment_content
            },
            format='json'
        )

        comment_updated = Comment.objects.get(id=self.comment.pk)

        self.assertEqual(comment_updated.content, new_comment_content)

    def test_was_edited_attribute_changed_to_true(self):
        """
        Should verify if the was_edited attribute changed to true
        """
        self.client.put(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        comment_updated = Comment.objects.get(id=self.comment.pk)

        self.assertTrue(comment_updated.was_edited)

    def test_comment_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the comment does not exist
        """
        self.comment.delete()

        response = self.client.put(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.put(
            self.url,
            {
                'content': ''
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('content')[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
