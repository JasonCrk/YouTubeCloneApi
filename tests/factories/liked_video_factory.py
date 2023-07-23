import factory

from apps.video.models import LikedVideo

from tests.factories.channel_factory import ChannelFactory
from tests.factories.video_factory import VideoFactory

class BaseLikedVideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LikedVideo

    channel = factory.SubFactory(ChannelFactory)
    video = factory.SubFactory(VideoFactory)


class LikeVideoFactory(BaseLikedVideoFactory):
    class Meta:
        model = LikedVideo

    liked = True


class DislikeVideoFactory(BaseLikedVideoFactory):
    class Meta:
        model = LikedVideo

    liked = False
