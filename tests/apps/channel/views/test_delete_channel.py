from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel


class TestDeleteChannel(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.url_name = 'delete_channel'

    def test_success_response(self):
        """
        Should return a success response if the channel has been deleted successfully
        """
        channel: Channel = ChannelFactory.create(user=self.user)
        url = reverse(self.url_name, kwargs={'channel_id': channel.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The channel has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_channel_has_been_deleted(self):
        """
        Should verify if the channel has been deleted successfully
        """
        channel: Channel = ChannelFactory.create(user=self.user)
        url = reverse(self.url_name, kwargs={'channel_id': channel.pk})

        self.client.delete(url)

        channel_deleted = Channel.objects.filter(id=channel.pk)

        self.assertFalse(channel_deleted.exists())

    def test_channel_does_not_exist(self):
        """
        Should return an error message if the channel does not exist
        """
        channel: Channel = ChannelFactory.create(user=self.user)
        url = reverse(self.url_name, kwargs={'channel_id': channel.pk})

        channel.delete()

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_wants_to_delete_the_channel_they_are_currently_on(self):
        """
        Should verify if the channel has been deleted successfully
        """
        url = reverse(self.url_name, kwargs={'channel_id': self.user.current_channel.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'Cannot delete a channel that is currently in use'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_wants_to_delete_a_channel_that_is_not_owned(self):
        """
        Should return an error message if the user wants to delete a channel that is not owned
        """
        channel: Channel = ChannelFactory.create()

        not_owned_channel_url = reverse(self.url_name, kwargs={'channel_id': channel.pk})

        response = self.client.delete(not_owned_channel_url)

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
