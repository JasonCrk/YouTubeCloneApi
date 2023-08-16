from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.link import LinkFactory

from apps.link.models import Link


class TestDeleteLink(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url_name = 'delete_link'

    def test_success_response(self):
        """
        Should return a success response if the link has been deleted
        """
        link: Link = LinkFactory.create(channel=self.user.current_channel)
        url = reverse(self.url_name, kwargs={'link_id': link.pk})

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The link has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_link_has_been_deleted(self):
        """
        Should verify if the link has been deleted successfully
        """
        link: Link = LinkFactory.create(channel=self.user.current_channel)
        url = reverse(self.url_name, kwargs={'link_id': link.pk})

        self.client.delete(url)

        link_deleted = Link.objects.filter(id=link.pk)

        self.assertFalse(link_deleted.exists())

    def test_link_does_not_exist(self):
        """
        Should verify if the link has been deleted successfully
        """
        link: Link = LinkFactory.create(channel=self.user.current_channel)
        url = reverse(self.url_name, kwargs={'link_id': link.pk})

        link.delete()

        response = self.client.delete(url)

        self.assertDictEqual(response.data, {'message': 'The link does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_channel_wants_to_delete_a_link_that_is_not_their_own(self):
        """
        Should return an error response and a 401 status code
        if a channel wants to delete a link that is not their own
        """
        not_own_link = LinkFactory.create()

        not_own_link_url = reverse(self.url_name, kwargs={'link_id': not_own_link.pk})

        response = self.client.delete(not_own_link_url)

        self.assertDictEqual(response.data, {'message': 'You do not own this link'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
