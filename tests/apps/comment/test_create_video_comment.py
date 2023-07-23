from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.video_factory import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestCreateVideoComment(TestSetup):
    def setUp(self):
        super().setUp()

        self.test_video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url = reverse('create_video_comment', kwargs={'video_id': self.test_video.pk})

    def test_to_return_success_response_if_the_creation_of_a_comment_to_a_video_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The comment has been created'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_to_check_if_comment_creation_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        comments_count = Comment.objects.filter(
            video=self.test_video,
            channel=self.user.current_channel
        ).count()

        self.assertEqual(comments_count, 1)

    def test_to_return_error_response_if_the_video_does_not_exists(self):
        url = reverse('create_video_comment', kwargs={'video_id': 1000})

        response = self.client.post(
            url,
            {
                'content': faker.paragraph()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'the video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
