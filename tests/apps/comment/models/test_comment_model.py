from django.test import TestCase

from tests.factories.comment import CommentFactory

from apps.comment.models import Comment


class TestCommentModel(TestCase):
    def setUp(self):
        self.comment: Comment = CommentFactory.create()

    def test_str_of_the_comment_model_is_the_owner_channel_name(self):
        """
        Should verify if the __str__() of the comment model is the owner channel name
        """
        self.assertEqual(self.comment.__str__(), self.comment.channel.name)

    def test_channel_has_been_created(self):
        """
        Should verify if the comment has been created
        """
        comment = Comment.objects.filter(id=self.comment.pk)
        self.assertTrue(comment.exists())
