from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel, ChannelSubscription

from faker import Faker

faker = Faker()


class TestSubscribeChannel(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.channel: Channel = ChannelFactory.create(user=self.user)

        self.url_name = 'subscribe_channel'

    def test_message_of_subscribe_to_channel(self):
        url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Subscription added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_channel_subscription(self):
        url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

        self.client.post(url)

        subscription = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel
        )

        self.assertTrue(subscription.exists())

    def test_message_of_remove_subscription(self):
        self.channel.subscriptions.add(self.user.current_channel)

        url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

        response = self.client.post(url)

        self.assertDictEqual(response.data, {'message': 'Subscription removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscription_has_been_removed(self):
        self.channel.subscriptions.add(self.user.current_channel)

        url = reverse(self.url_name, kwargs={'channel_id': self.channel.pk})

        self.client.post(url)

        subscription_exists = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel
        ).exists()

        self.assertFalse(subscription_exists)

    def test_channel_does_not_exists(self):
        non_exist_channel_id = self.channel.pk

        self.channel.delete()

        non_exist_channel_url = reverse(self.url_name, kwargs={'channel_id': non_exist_channel_id})

        response = self.client.post(non_exist_channel_url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_wants_to_subscribe_a_itself_channel(self):
        user_channel_url = reverse(self.url_name, kwargs={'channel_id': self.user.current_channel.pk})

        response = self.client.post(user_channel_url)

        self.assertDictEqual(response.data, {'message': "Can't subscribe to itself"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
