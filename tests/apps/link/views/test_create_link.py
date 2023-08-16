from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestCreateLink(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.url = reverse('create_link')

    def test_success_response(self):
        """
        Should return a success response if the link has been created
        """
        response = self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link has been created'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_link_has_been_created(self):
        """
        Should verify if the link has been created successfully
        """
        self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        channel_links = Link.objects.filter(channel=self.user.current_channel)

        self.assertEqual(channel_links.count(), 1)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.pystr()
            }
        )

        self.assertIsNotNone(response.data.get('errors').get('url')[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
