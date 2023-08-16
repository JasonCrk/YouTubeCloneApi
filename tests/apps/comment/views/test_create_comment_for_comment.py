from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.comment import CommentFactory

from apps.comment.models import Comment

from faker import Faker

faker = Faker()


class TestCreateCommentForComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.comment: Comment = CommentFactory.create(channel=self.user.current_channel)
        self.url = reverse('create_comment_for_comment', kwargs={'comment_id': self.comment.pk})

    def test_success_response(self):
        """
        Should return a success response if the comment has been created
        """
        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment has been created'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_comment_has_been_created(self):
        """
        Should verify if the comment has been created successfully
        """
        self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        comments_of_comment = Comment.objects.filter(comment=self.comment)

        self.assertEqual(comments_of_comment.count(), 1)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.post(
            self.url,
            {
                'content': ''
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('content')[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_parent_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the comment parent does not exist
        """
        self.comment.delete()

        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment parent does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
