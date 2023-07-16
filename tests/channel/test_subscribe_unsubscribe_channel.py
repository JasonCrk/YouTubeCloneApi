from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from apps.channel.models import Channel, ChannelSubscription
from apps.user.models import UserAccount

from faker import Faker


class TestSubscribeAndUnsubscribeChannel(TestSetup):
    def setUp(self):
        super().setUp()

        faker = Faker()

        user_1 = UserAccount.objects.create_user(
            username='TestMan1',
            email=faker.email(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password='AccountTestPassword1'
        )

        self.user_2 = UserAccount.objects.create_user(
            username='TestMan2',
            email=faker.email(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password='AccountTestPassword2'
        )

        self.url = reverse('subscribe_unsubscribe_channel')

        self.channel_not_subscribed = Channel.objects.get(user=user_1)

        self.channel_subscribed = Channel.objects.get(user=self.user_2)
        self.channel_subscribed.subscriptions.add(self.user.current_channel)

    def test_successful_subscription_message(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel_not_subscribed.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription added'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_has_subscribed_successfully(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.channel_not_subscribed.pk
            },
            format='json'
        )

        subscription_exists = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel_not_subscribed
        ).exists()

        self.assertEqual(subscription_exists, True)

    def test_unsubscribe_message_successfully(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel_subscribed.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'Subscription removed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_unsubscribed_from_the_channel_successfully(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.channel_subscribed.pk
            },
            format='json'
        )

        subscribe = ChannelSubscription.objects.filter(
            subscriber=self.user.current_channel,
            subscribing=self.channel_not_subscribed
        )

        self.assertFalse(subscribe.exists())

    def test_channel_id_is_not_number(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': 'test_id'
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

    def test_user_cannot_subscribe_to_own_channel(self):
        my_channel = Channel.objects.get(user=self.user)

        response = self.client.post(
            self.url,
            {
                'channel_id': my_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': "You can't subscribe to a channel that's yours"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
