from django.test import TestCase

from tests.factories.channel import ChannelSubscriptionFactory

from apps.channel.models import ChannelSubscription


class TestChannelSubscriptionModel(TestCase):
    def setUp(self):
        self.channel_subscription: ChannelSubscription = ChannelSubscriptionFactory.create()

    def test_str_of_the_channel_subscription_model_is_the_subscriber_name(self):
        """
        Should verify if the __str__() of the channel subscription model is the subscriber name
        """
        self.assertEqual(self.channel_subscription.__str__(), self.channel_subscription.subscriber.name)

    def test_channel_subscription_has_been_created(self):
        """
        Should verify if the channel subscription has been created
        """
        channel_subscription = ChannelSubscription.objects.filter(id=self.channel_subscription.pk)
        self.assertTrue(channel_subscription.exists())
