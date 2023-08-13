from django.test import TestCase

from tests.factories.video import LikeVideoFactory

from apps.video.models import LikedVideo


class TestLikedVideoModel(TestCase):
    def setUp(self):
        self.like_video: LikedVideo = LikeVideoFactory.create()

    def test_str_of_the_liked_video_model_is_the_channel_name(self):
        """
        Should verify if the __str__() of the liked video model is the channel name
        """
        self.assertEqual(self.like_video.__str__(), self.like_video.channel.name)

    def test_liked_video_has_been_created(self):
        """
        Should verify if the liked video has been created
        """
        like_video = LikedVideo.objects.filter(id=self.like_video.pk)
        self.assertTrue(like_video.exists())
