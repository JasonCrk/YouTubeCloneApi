import factory

from apps.video.models import VideoView

from tests.factories.channel_factory import ChannelFactory
from tests.factories.video_factory import VideoFactory


class VideoViewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VideoView

    channel = factory.SubFactory(ChannelFactory)
    video = factory.SubFactory(VideoFactory)
    count = factory.Faker('random_digit_not_null')
