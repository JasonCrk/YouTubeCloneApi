import factory

from apps.playlist.models import Playlist, PlaylistVideo

from tests.factories.channel_factory import ChannelFactory
from tests.factories.video_factory import VideoFactory


class PlaylistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Playlist

    channel = factory.SubFactory(ChannelFactory)
    thumbnail = factory.Faker('image_url')
    name = factory.Faker('pystr')
    description = factory.Faker('paragraph')


class PlaylistVideoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlaylistVideo

    video = factory.SubFactory(VideoFactory)
    playlist = factory.SubFactory(PlaylistFactory)
