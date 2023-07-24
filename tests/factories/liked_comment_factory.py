import factory

from tests.factories.channel_factory import ChannelFactory
from tests.factories.comment_factory import CommentFactory

from apps.comment.models import LikedComment


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
