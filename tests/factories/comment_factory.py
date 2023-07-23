import factory

from apps.comment.models import Comment

from tests.factories.channel_factory import ChannelFactory
from tests.factories.video_factory import VideoFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    video = factory.SubFactory(VideoFactory)
    channel = factory.SubFactory(ChannelFactory)
    content = factory.Faker('paragraph')
