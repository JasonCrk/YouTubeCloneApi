from django.test import TestCase

from faker import Faker

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel

faker = Faker()


class TestChannelModel(TestCase):
    def setUp(self):
        self.channel: Channel = ChannelFactory.create()

    def test_str_of_the_channel_subscription_model_is_the_subscriber_name(self):
        """
        Should verify if the __str__() of the channel model is the channel name
        """
        self.assertEqual(self.channel.__str__(), self.channel.name)

    def test_channel_has_been_created(self):
        """
        Should verify if the channel has been created
        """
        channel_exists = Channel.objects.filter(id=self.channel.pk)
        self.assertTrue(channel_exists)
