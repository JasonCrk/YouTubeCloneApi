from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth
from tests.factories.channel import ChannelFactory

from apps.channel.models import Channel

from faker import Faker

faker = Faker()


class TestCreateChannel(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('create_channel')

    def test_success_response(self):
        """
        Should return a success response if the channel has been created successfully
        """
        response = self.client.post(
            self.url,
            {
                'name': faker.name()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The channel has been created'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_channel_has_been_created(self):
        """
        Should verify if channel has been created successfully
        """
        self.client.post(
            self.url,
            {
                'name': faker.name()
            },
            format='json'
        )

        user_channel = Channel.objects.filter(user=self.user)

        self.assertEqual(user_channel.count(), 2)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response if the data sent is invalid
        """
        response = self.client.post(
            self.url,
            {
                'name': ''
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('name'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_have_more_than_10_channels(self):
        """
        Should return an error message and a 400 status code if the user wants to have more than 10 channels
        """
        ChannelFactory.create_batch(9, user=self.user)

        response = self.client.post(
            self.url,
            {
                'name': faker.name()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': "You can't have more than 10 channels"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
