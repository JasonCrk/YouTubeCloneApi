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

        test_user_1 = UserAccount.objects.create_user(
            email=faker.email(),
            username=faker.name(),
            first_name='Account2',
            last_name='Test2',
            password='AccountTestPassword2'
        )

        self.test_user_2 = UserAccount.objects.create_user(
            email=faker.email(),
            username=faker.name(),
            first_name='Account2',
            last_name='Test2',
            password='AccountTestPassword2'
        )

        self.url = reverse('subscribe_unsubscribe_channel')

        self.channel_not_subscribed = Channel.objects.get(user=test_user_1)

        self.channel_subscribed = Channel.objects.get(user=self.test_user_2)
        self.channel_subscribed.subscription.add(self.user)


    def test_successful_subscription_message(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel_not_subscribed.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, { 'message': 'Subscription added' })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_has_subscribed_successfully(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.channel_not_subscribed.pk
            },
            format='json'
        )

        subscribe = ChannelSubscription.objects.filter(user=self.user, channel=self.channel_not_subscribed)

        self.assertEqual(subscribe.exists(), True)

    def test_unsubscribe_message_successfully(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel_subscribed.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, { 'message': 'Subscription removed' })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_the_user_unsubscribed_from_the_channel_successfully(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.channel_subscribed.pk
            },
            format='json'
        )

        subscribe = ChannelSubscription.objects.filter(user=self.user, channel=self.channel_subscribed)

        self.assertFalse(subscribe.exists())

    def test_is_not_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='')

        response = self.client.post(
            self.url,
            {
                'channel_id': self.channel_not_subscribed.pk
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_channel_id_is_not_number(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': 'test_id'
            },
            format='json'
        )

        self.assertDictEqual(response.data, { 'message': 'The channel ID must be a number' })
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_channel_is_does_not_exist(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': 10
            },
            format='json'
        )

        self.assertDictEqual(response.data, { 'message': 'The channel does not exist' })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
