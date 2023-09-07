from django.test import TestCase

from tests.factories.video import VideoViewFactory

from apps.video.models import VideoView


class TestVideoViewModel(TestCase):
    def test_str_of_the_video_view_model_is_the_channel_name(self):
        """
        Should verify if the __str__() of the video view model is the channel name when is not null
        """
        self.video_view: VideoView = VideoViewFactory.create()

        self.assertEqual(self.video_view.__str__(), self.video_view.channel.name)

    def test_str_of_the_video_view_model_is_the_video_title(self):
        """
        Should verify if the __str__() of the video view model is the video title when the channel name is null
        """
        self.video_view: VideoView = VideoViewFactory.create(channel=None)

        self.assertEqual(self.video_view.__str__(), self.video_view.video.title)

    def test_video_view_has_been_created(self):
        """
        Should verify if the video view has been created
        """
        self.video_view: VideoView = VideoViewFactory.create()

        video_view = VideoView.objects.filter(id=self.video_view.pk)
        self.assertTrue(video_view.exists())
