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

        self.url = reverse('subscribe_channel')

        self.channel: Channel = ChannelFactory.create(user=self.user)

    def test_message_of_subscribe_to_channel(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_check_channel_subscription(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.channel.pk
            },
            format='json'
        )

        subscription = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel
        )

        self.assertTrue(subscription.exists())

    def test_message_of_remove_subscription(self):
        self.channel.subscriptions.add(self.user.current_channel)

        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscription_has_been_removed(self):
        self.channel.subscriptions.add(self.user.current_channel)

        self.client.post(
            self.url,
            {
                'channel_id': self.channel.pk
            },
            format='json'
        )

        subscription_exists = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel
        ).exists()

        self.assertFalse(subscription_exists)

    def test_channel_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': faker.pystr(max_chars=8)
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_channel_does_not_exists(self):
        non_exist_channel_id = self.channel.pk

        self.channel.delete()

        response = self.client.post(
            self.url,
            {
                'channel_id': non_exist_channel_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_wants_to_subscribe_a_itself_channel(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.user.current_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': "Can't subscribe to itself"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
