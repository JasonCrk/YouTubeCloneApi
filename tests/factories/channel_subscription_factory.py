import factory

from tests.factories.channel_factory import ChannelFactory

from apps.channel.models import ChannelSubscription


class ChannelSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChannelSubscription

    subscriber = factory.SubFactory(ChannelFactory)
    subscribing = factory.SubFactory(ChannelFactory)
