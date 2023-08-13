from django.test import TestCase

from tests.factories.video import VideoFactory

from apps.video.models import Video


class TestVideoModel(TestCase):
    def setUp(self):
        self.video: Video = VideoFactory.create()

    def test_str_of_the_video_model_is_the_video_title(self):
        """
        Should verify if the __str__() of the video model is the video title
        """
        self.assertEqual(self.video.__str__(), self.video.title)

    def test_video_has_been_created(self):
        """
        Should verify if the video has been created
        """
        video = Video.objects.filter(id=self.video.pk)
        self.assertTrue(video.exists())

    def test_order_by_video_title_alphabetically_by_default(self):
        """
        Should verify that the videos are arranged alphabetically by video title
        """
        VideoFactory.create_batch(3)

        videos = list(Video.objects.all().values('id', 'title'))

        videos_sorted_alphabetically = sorted(videos, key=lambda video: video.get('title'))

        for index, video in enumerate(videos_sorted_alphabetically):
            self.assertEqual(videos[index].get('id'), video.get('id'))
