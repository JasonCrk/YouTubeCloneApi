import factory

from apps.video.models import LikedVideo

from tests.factories.ChannelFactory import ChannelFactory
from tests.factories.VideoFactory import VideoFactory

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
