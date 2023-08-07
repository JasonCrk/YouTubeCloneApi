from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.channel import ChannelFactory, ChannelSubscriptionFactory

from apps.channel.models import Channel


class TestSubscribedChannels(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('subscribed_channels')

        self.channels_subscribed: list[Channel] = ChannelFactory.create_batch(2, user=self.user)
        for channel_subscribed in self.channels_subscribed:
            ChannelSubscriptionFactory.create(
                subscriber=self.user.current_channel,
                subscribing=channel_subscribed
            )

        self.channel_without_subscribers = ChannelFactory.create(user=self.user)

    def test_to_return_all_channels_subscribed_successful(self):
        response = self.client.get(self.url)

        response_channels = list(map(lambda channel: dict(channel), response.data.get('data')))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for index, channel_subscribed in enumerate(self.channels_subscribed):
            self.assertEqual(
                channel_subscribed.pk,
                response_channels[index].get('id')
            )
