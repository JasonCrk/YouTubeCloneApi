from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.link_factory import LinkFactory

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestEditLink(TestSetup):
    def setUp(self):
        super().setUp()
        self.url_name = 'edit_link'

        self.test_link: Link = LinkFactory.create(channel=self.user.current_channel)

    def test_to_return_success_response_if_the_link_has_been_updated_successfully(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        response = self.client.put(
            url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_link_title_has_been_updated_successfully(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        test_link_title = faker.pystr(max_chars=15)

        self.client.put(
            url,
            {
                'title': test_link_title,
                'url': self.test_link.url
            },
            format='json'
        )

        test_link_updated: Link = Link.objects.get(id=self.test_link.pk)

        self.assertEqual(test_link_updated.title, test_link_title)

    def test_to_check_if_the_link_url_has_been_updated_successfully(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        test_link_url = faker.url()

        self.client.put(
            url,
            {
                'title': self.test_link.title,
                'url': test_link_url
            },
            format='json'
        )

        test_link_updated: Link = Link.objects.get(id=self.test_link.pk)

        self.assertEqual(test_link_updated.url, test_link_url)

    def test_to_return_error_response_and_status_code_404_if_the_link_does_not_exists(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        self.test_link.delete()

        response = self.client.put(
            url,
            {
                'title': faker.pystr(max_chars=15),
                'url': self.test_link.url
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_401_if_a_channel_wants_to_edit_a_link_that_is_not_their_own(self):
        not_own_test_link: Link = LinkFactory.create()

        url = reverse(self.url_name, kwargs={'link_id': not_own_test_link.pk})

        response = self.client.put(
            url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You do not own this link'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_and_status_code_400_if_the_link_url_is_not_a_url(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        response = self.client.put(
            url,
            {
                'title': self.test_link.title,
                'url': faker.pystr()
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('url'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_link_title_exceeds_15_characters(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        response = self.client.put(
            url,
            {
                'title': faker.pystr(min_chars=16, max_chars=17),
                'url': self.test_link.url
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('title'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_link_url_is_blank(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        response = self.client.put(
            url,
            {
                'title': faker.pystr(max_chars=15)
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('url'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_link_title_is_blank(self):
        url = reverse(self.url_name, kwargs={'link_id': self.test_link.pk})

        response = self.client.put(
            url,
            {
                'url': faker.url()
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('title'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
