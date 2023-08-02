import factory

from apps.link.models import Link

from tests.factories.channel_factory import ChannelFactory


class LinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Link

    title = factory.Faker('pystr', max_chars=15)
    url = factory.Faker('url')
    channel = factory.SubFactory(ChannelFactory)
