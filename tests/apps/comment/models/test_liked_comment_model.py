from django.test import TestCase

from tests.factories.comment import LikeCommentFactory

from apps.comment.models import LikedComment


class TestLikedCommentModel(TestCase):
    def setUp(self):
        self.like_comment: LikedComment = LikeCommentFactory.create()

    def test_str_of_the_comment_model_is_the_owner_channel_name(self):
        """
        Should verify if the __str__() of the like comment model is the owner channel name
        """
        self.assertEqual(self.like_comment.__str__(), self.like_comment.channel.name)

    def test_like_comment_has_been_created(self):
        """
        Should verify if the like comment has been created
        """
        like_comment = LikedComment.objects.filter(id=self.like_comment.pk)
        self.assertTrue(like_comment.exists())
