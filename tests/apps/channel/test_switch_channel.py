from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.ChannelFactory import ChannelFactory
from tests.factories.UserAccountFactory import UserFactory

from apps.channel.models import Channel
from apps.user.models import UserAccount

from faker import Faker

faker = Faker()


class TestSwitchChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('switch_channel')

        self.second_channel: Channel = ChannelFactory.create(user=self.user)

    def test_to_return_success_response_if_switch_channel_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': self.second_channel.pk
            },
            format='json'
        )

        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_switch_channel_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'channel_id': self.second_channel.pk
            },
            format='json'
        )

        user: UserAccount = UserAccount.objects.get(id=self.user.pk)

        self.assertEqual(user.current_channel.pk, self.second_channel.pk)

    def test_to_return_error_response_if_the_channel_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_channel_does_not_exist(self):
        response = self.client.post(
            self.url,
            {
                'channel_id': 100
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_user_wants_to_switch_channel_that_they_dont_own(self):
        test_user: UserAccount = UserFactory.create()

        not_own_channel: Channel = Channel.objects.get(user=test_user)

        response = self.client.post(
            self.url,
            {
                'channel_id': not_own_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
