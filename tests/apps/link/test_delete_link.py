from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.link_factory import LinkFactory

from apps.link.models import Link


class TestDeleteLink(TestSetup):
    def setUp(self):
        super().setUp()

        self.test_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.url = reverse('delete_link', kwargs={'link_id': self.test_link.pk})

    def test_to_return_success_response_if_the_link_has_been_deleted_successfully(self):
        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The link has been deleted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_link_has_been_deleted_successfully(self):
        self.client.delete(self.url)

        test_link_deleted_exists = Link.objects.filter(id=self.test_link.pk).exists()

        self.assertFalse(test_link_deleted_exists)

    def test_to_check_if_the_link_positions_have_been_fixed_after_deleting_a_link(self):
        second_test_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.delete(self.url)

        second_test_link_updated: Link = Link.objects.get(id=second_test_link.pk)

        self.assertEqual(
            second_test_link.position - 1,
            second_test_link_updated.position
        )

    def test_to_return_error_response_and_status_code_404_if_the_link_does_not_exists(self):
        self.test_link.delete()

        response = self.client.delete(self.url)

        self.assertDictEqual(response.data, {'message': 'The link does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_401_if_a_channel_wants_to_delete_a_link_that_is_not_their_own(self):
        not_own_link = LinkFactory.create()

        not_own_link_url = reverse('delete_link', kwargs={'link_id': not_own_link.pk})

        response = self.client.delete(not_own_link_url)

        self.assertDictEqual(response.data, {'message': 'You do not own this link'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
