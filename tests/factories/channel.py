import factory

from apps.channel.models import Channel, ChannelSubscription

from tests.factories.user_account import BaseUserFactory


class ChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Channel

    banner_url = factory.Faker('image_url')
    picture_url = factory.Faker('image_url')
    user = factory.SubFactory(BaseUserFactory)
    name = factory.Faker('name')
    contact_email = factory.Faker('email')


class ChannelSubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChannelSubscription

    subscriber = factory.SubFactory(ChannelFactory)
    subscribing = factory.SubFactory(ChannelFactory)
