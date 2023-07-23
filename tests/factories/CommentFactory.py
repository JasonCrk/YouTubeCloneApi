import factory

from apps.comment.models import Comment

from tests.factories.ChannelFactory import ChannelFactory
from tests.factories.VideoFactory import VideoFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    video = factory.SubFactory(VideoFactory)
    channel = factory.SubFactory(ChannelFactory)
    content = factory.Faker('paragraph')
