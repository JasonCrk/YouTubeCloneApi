from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.link import LinkFactory

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestEditLink(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()
        self.link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.url_name = 'edit_link'
        self.url = reverse(self.url_name, kwargs={'link_id': self.link.pk})

    def test_success_response(self):
        """
        Should return a success response if the link has been updated
        """
        response = self.client.put(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_link_title_has_been_updated(self):
        """
        Should verify if the link title has been updated
        """
        link_title = faker.pystr(max_chars=15)

        self.client.put(
            self.url,
            {
                'title': link_title,
                'url': self.link.url
            },
            format='json'
        )

        link_updated: Link = Link.objects.get(id=self.link.pk)

        self.assertEqual(link_updated.title, link_title)

    def test_link_url_has_been_updated(self):
        """
        Should verify if the link url has been updated
        """
        link_url = faker.url()

        self.client.put(
            self.url,
            {
                'title': self.link.title,
                'url': link_url
            },
            format='json'
        )

        link_updated: Link = Link.objects.get(id=self.link.pk)

        self.assertEqual(link_updated.url, link_url)

    def test_link_does_not_exist(self):
        """
        Should return an error response and a 404 status code if the link does not exist
        """
        self.link.delete()

        response = self.client.put(
            self.url,
            {
                'title': faker.pystr(max_chars=15),
                'url': self.link.url
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_channel_wants_to_edit_a_link_that_is_not_their_own(self):
        """
        Should return an error response and a 401 status code if a channel wants to edit a link that is not their own
        """
        not_own_link: Link = LinkFactory.create()

        not_own_link_url = reverse(self.url_name, kwargs={'link_id': not_own_link.pk})

        response = self.client.put(
            not_own_link_url,
            {
                'title': faker.pystr(max_chars=15),
                'url': faker.url()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You do not own this link'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        response = self.client.put(
            self.url,
            {
                'title': self.link.title,
                'url': faker.pystr()
            },
            format='json'
        )

        self.assertIsNotNone(response.data.get('errors').get('url')[0])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
