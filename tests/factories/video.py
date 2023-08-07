from datetime import datetime

import factory

from apps.video.models import Video, LikedVideo, VideoView

from tests.factories.channel import ChannelFactory


class VideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Video

    title = factory.Faker('pystr', max_chars=45)
    video_url = factory.Faker('url')
    thumbnail = factory.Faker('image_url')
    description = factory.Faker('paragraph')
    channel = factory.SubFactory(ChannelFactory)
    publication_date = datetime.today()


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


class VideoViewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VideoView

    channel = factory.SubFactory(ChannelFactory)
    video = factory.SubFactory(VideoFactory)
    count = factory.Faker('random_digit_not_null')
