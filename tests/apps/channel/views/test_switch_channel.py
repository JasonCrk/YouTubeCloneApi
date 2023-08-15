from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel
from apps.user.models import UserAccount

from faker import Faker

faker = Faker()


class TestSwitchChannel(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('switch_channel')

        self.second_channel: Channel = ChannelFactory.create(user=self.user)

    def test_success_response(self):
        """
        Should return a 204 status code if the switch channel has been successful
        """
        response = self.client.post(
            self.url,
            {
                'channel_id': self.second_channel.pk
            },
            format='json'
        )

        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_switch_channel_successfully(self):
        """
        Should verify that switch channel has been successful
        """
        self.client.post(
            self.url,
            {
                'channel_id': self.second_channel.pk
            },
            format='json'
        )

        user: UserAccount = UserAccount.objects.get(id=self.user.pk)

        self.assertEqual(user.current_channel.pk, self.second_channel.pk)

    def test_channel_id_is_not_a_number(self):
        """
        Should return an error response if the channel ID is not a number
        """
        response = self.client.post(
            self.url,
            {
                'channel_id': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_channel_does_not_exist(self):
        """
        Should return an error response if the channel does not exist
        """
        non_exists_channel_id = self.second_channel.pk

        self.second_channel.delete()

        response = self.client.post(
            self.url,
            {
                'channel_id': non_exists_channel_id
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_wants_to_switch_channel_with_a_channel_that_is_dont_owned(self):
        """
        Should return an error response if a user wants to switch channel with a channel that is down owned
        """
        not_own_channel: Channel = ChannelFactory.create()

        response = self.client.post(
            self.url,
            {
                'channel_id': not_own_channel.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
