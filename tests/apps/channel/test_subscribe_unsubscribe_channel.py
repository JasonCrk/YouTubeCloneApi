from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.channel_factory import ChannelFactory

from apps.channel.models import Channel, ChannelSubscription

from faker import Faker

faker = Faker()


class TestSubscribeAndUnsubscribeChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('subscribe_unsubscribe_channel')

        self.test_channel: Channel = ChannelFactory.create(user=self.user)

    def test_successful_subscription_message(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.test_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_has_subscribed_successfully(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.test_channel.pk
            },
            format='json'
        )

        subscription_exists = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.test_channel
        ).exists()

        self.assertTrue(subscription_exists)

    def test_unsubscribe_message_successfully(self):
        self.test_channel.subscriptions.add(self.user.current_channel)

        response = self.client.post(
            self.url,
            {
                'channel_id': self.test_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_unsubscribed_from_the_channel_successfully(self):
        self.test_channel.subscriptions.add(self.user.current_channel)

        self.client.post(
            self.url,
            {
                'channel_id': self.test_channel.pk
            },
            format='json'
        )

        subscription_exists = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.test_channel
        ).exists()

        self.assertFalse(subscription_exists)

    def test_channel_id_is_not_number(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': faker.pystr(max_chars=8)
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_channel_is_does_not_exist(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': 1000
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_subscribe_to_itself(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.user.current_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': "Can't subscribe to itself"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
