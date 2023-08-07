from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.link import LinkFactory

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestCreateLink(TestSetup):
    def setUp(self):
        super().setUp()
        self.url = reverse('create_link')

    def test_to_return_success_response_if_the_link_creation_has_been_successful(self):
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

    def test_to_check_if_the_link_creation_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        channel_links_count = Link.objects.filter(channel=self.user.current_channel).count()

        self.assertEqual(channel_links_count, 1)

    def test_to_check_if_the_link_position_is_successive(self):
        LinkFactory.create_batch(3, channel=self.user.current_channel)

        link_data = {
            'title': faker.pystr(max_chars=15),
            'url': faker.url()
        }

        self.client.post(
            self.url,
            link_data,
            format='json'
        )

        channel_link = Link.objects.filter(
            title=link_data['title'],
            url=link_data['url'],
            channel=self.user.current_channel
        ).first()

        self.assertEqual(channel_link.position, 3)

    def test_to_return_error_response_if_the_link_url_is_not_a_url(self):
        response = self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.pystr()
            }
        )

        self.assertIsNotNone(response.data.get('errors').get('url'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_link_title_exceed_15_characters(self):
        response = self.client.post(
            self.url,
            {
                'title': faker.pystr(min_chars=16, max_chars=17),
                'url': faker.url()
            }
        )

        self.assertIsNotNone(response.data.get('errors').get('title'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_link_title_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'url': faker.url()
            }
        )

        self.assertIsNotNone(response.data.get('errors').get('title'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_link_url_is_blank(self):
        response = self.client.post(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
            }
        )

        self.assertIsNotNone(response.data.get('errors').get('url'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
