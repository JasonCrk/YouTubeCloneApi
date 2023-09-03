from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from tests.factories.comment import CommentFactory, DislikeCommentFactory, LikeCommentFactory
from tests.factories.video import VideoFactory

from apps.comment.models import Comment
from apps.video.models import Video

from apps.comment.serializers import CommentListSerializer

from youtube_clone.enums import CommentSortOptions


class TestRetrieveVideoComments(APITestCase):
    def setUp(self):
        self.video: Video = VideoFactory.create()

        self.url = reverse('video_comments', kwargs={'video_id': self.video.pk})

    def test_return_success_status_code(self):
        """
        Should return a 200 status code if the comments could be retrieved successfully
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_the_video_comments(self):
        """
        Should return the video comment successfully
        """
        expected_comment: Comment = CommentFactory.create(video=self.video)
        not_expected_comment: Comment = CommentFactory.create()

        response = self.client.get(self.url)

        retrieved_comments_ids = [dict(comment).get('id') for comment in response.data.get('data')]

        self.assertIn(expected_comment.pk, retrieved_comments_ids)
        self.assertNotIn(not_expected_comment.pk, retrieved_comments_ids)

    def test_serialized_video_comments(self):
        """
        Should verify than return a serialized video comment
        """
        video_comment = CommentFactory.create(video=self.video)

        response = self.client.get(self.url)

        serialized_video_comment = CommentListSerializer(
            video_comment,
            context={'request': response.wsgi_request}
        )

        first_retrieved_comment = dict(response.data.get('data')[0])

        self.assertEqual(
            first_retrieved_comment,
            serialized_video_comment.data
        )

    def test_sort_by_TOP_COMMENTS(self):
        """
        Should return the video comments sorted by TOP_COMMENTS (order from highest to lowest according to the number of likes a comment has)
        """
        comment_without_likes: Comment = CommentFactory.create(video=self.video)

        second_comment_with_most_likes: Comment = CommentFactory.create(video=self.video)
        LikeCommentFactory.create(comment=second_comment_with_most_likes)

        first_comment_with_most_likes: Comment = CommentFactory.create(video=self.video)
        LikeCommentFactory.create_batch(2, comment=first_comment_with_most_likes)

        response = self.client.get(self.url, {'sort_by': CommentSortOptions.TOP_COMMENTS.value})

        retrieved_comments_ids = [dict(comment).get('id') for comment in response.data.get('data')]

        self.assertEqual(retrieved_comments_ids[0], first_comment_with_most_likes.pk)
        self.assertEqual(retrieved_comments_ids[1], second_comment_with_most_likes.pk)
        self.assertEqual(retrieved_comments_ids[2], comment_without_likes.pk)

    def test_sort_by_TOP_COMMENTS_ignoring_dislikes(self):
        """
        Should verify that it returns the video comment sorted by TOP_COMMENTS ignoring the dislikes that the comment has
        """
        comment_with_most_dislikes: Comment = CommentFactory.create(video=self.video)
        DislikeCommentFactory.create_batch(2, comment=comment_with_most_dislikes)

        comment_with_most_likes: Comment = CommentFactory.create(video=self.video)
        LikeCommentFactory.create(comment=comment_with_most_likes)

        response = self.client.get(self.url, {'sort_by': CommentSortOptions.TOP_COMMENTS.value})

        retrieved_comments_ids = [dict(comment).get('id') for comment in response.data.get('data')]

        self.assertEqual(retrieved_comments_ids[0], comment_with_most_likes.pk)
        self.assertEqual(retrieved_comments_ids[1], comment_with_most_dislikes.pk)

    def test_sort_by_NEWEST_FIRST(self):
        """
        Should return the video comments sorted by NEWEST_FIRST
        """
        video_comments: list[Comment] = CommentFactory.create_batch(3, video=self.video)

        response = self.client.get(self.url, {'sort_by': CommentSortOptions.NEWEST_FIRST.value})

        retrieved_comments_ids = [dict(comment).get('id') for comment in response.data.get('data')]

        for i, video in enumerate(video_comments):
            self.assertEqual(video.pk, retrieved_comments_ids[i])

    def test_default_sort_by_NEWEST_FIRST(self):
        """
        Should return the video comments sorted by NEWEST_FIRST 
        """
        video_comments: list[Comment] = CommentFactory.create_batch(3, video=self.video)

        response = self.client.get(self.url)

        retrieved_comments_ids = [dict(comment).get('id') for comment in response.data.get('data')]

        for i, video in enumerate(video_comments):
            self.assertEqual(video.pk, retrieved_comments_ids[i])

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.get(self.url)

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
