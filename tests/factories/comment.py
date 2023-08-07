import factory

from apps.comment.models import Comment, LikedComment

from tests.factories.channel import ChannelFactory
from tests.factories.video import VideoFactory


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    video = factory.SubFactory(VideoFactory)
    channel = factory.SubFactory(ChannelFactory)
    content = factory.Faker('paragraph')


class BaseLikedCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LikedComment

    channel = factory.SubFactory(ChannelFactory)
    comment = factory.SubFactory(CommentFactory)


class LikeCommentFactory(BaseLikedCommentFactory):
    class Meta:
        model = LikedComment

    liked = True


class DislikeCommentFactory(BaseLikedCommentFactory):
    class Meta:
        model = LikedComment

    liked = False