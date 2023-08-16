from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestCreateVideoComment(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url_name = 'create_video_comment'
        self.url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

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

        comments_count = Comment.objects.filter(
            video=self.video,
            channel=self.user.current_channel
        ).count()

        self.assertEqual(comments_count, 1)

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'the video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

        self.assertIsNotNone(response.data.get('errors').get('content'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
