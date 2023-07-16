from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from apps.channel.models import Channel


class TestCreateChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('create_channel')

    def test_to_return_success_response_if_the_channel_has_been_created(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Test name'
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel has been created'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_channel_has_been_created_correctly(self):
        self.client.post(
            self.url,
            {
                'name': 'Test name'
            },
            format='json'
        )

        user_channel_count = Channel.objects.filter(user=self.user).count()

        self.assertEqual(user_channel_count, 2)

    def test_to_return_error_response_if_the_name_send_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'name': ''
            },
            format='json'
        )

        self.assertNotEqual(response.data.get('errors').get('name'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_name_send_is_too_long(self):
        response = self.client.post(
            self.url,
            {
                'name': 'test name test name test name'
            },
            format='json'
        )

        self.assertNotEqual(response.data.get('errors').get('name'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_user_has_10_channels(self):
        for _ in range(9):
            Channel.objects.create(
                name=self.user.username,
                user=self.user
            ).save()

        response = self.client.post(
            self.url,
            {
                'name': 'Test name'
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': "You can't have more than 10 channels"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
