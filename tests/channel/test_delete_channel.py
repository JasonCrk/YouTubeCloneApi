from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from apps.user.models import UserAccount
from apps.channel.models import Channel


class TestDeleteChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.test_channel = Channel.objects.create(handle='test handle', user=self.user)

        self.url = reverse('delete_channel', kwargs={'channel_id': self.test_channel.pk})

    def test_to_return_error_response_if_the_user_wants_to_delete_their_only_channel(self):
        channel = Channel.objects.get(user=self.user, handle=self.user.username)
        channel.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': "You can't delete your last channel"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_success_response_if_the_channel_has_been_deleted(self):
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The channel has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_an_error_response_if_the_user_wants_to_delete_a_channel_that_they_dont_own(self):
        from faker import Faker

        faker = Faker()

        test_user = UserAccount.objects.create_user(
            email=faker.email(),
            username='TestManDeleteChannel',
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            password='AccountTestPassword'
        )

        channel = Channel.objects.get(user__pk=test_user.pk)

        url = reverse('delete_channel', kwargs={'channel_id': channel.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_check_that_the_channel_has_been_deleted(self):
        self.client.delete(self.url)

        channel_exist = Channel.objects.filter(id=self.test_channel.pk).exists()

        self.assertFalse(channel_exist)

    def test_to_return_error_response_if_the_channel_does_not_exist(self):
        url = reverse('delete_channel', kwargs={'channel_id': 12})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
