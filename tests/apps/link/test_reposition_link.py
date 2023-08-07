from django.urls import reverse

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.link import LinkFactory

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestRepositionLink(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('reposition_link')

        self.first_link: Link = LinkFactory.create(channel=self.user.current_channel)
        self.second_link: Link = LinkFactory.create(channel=self.user.current_channel)
        self.third_link: Link = LinkFactory.create(channel=self.user.current_channel)
        self.fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)

    def test_to_return_success_response_if_the_link_position_change_has_been_successful(self):
        response = self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': self.second_link.position
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link has been repositioned'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_change_of_position_of_the_first_link_to_the_position_of_the_second_link_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': self.second_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)
        second_link_updated: Link = Link.objects.get(id=self.second_link.pk)

        self.assertEqual(self.first_link.position, second_link_updated.position)
        self.assertEqual(self.second_link.position, first_link_updated.position)

    def test_to_check_if_the_change_of_position_of_the_first_link_to_the_position_of_the_fourth_link_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': self.fourth_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)

        self.assertEqual(first_link_updated.position, self.fourth_link.position)

    def test_to_check_if_the_links_are_arranged_correctly_after_changing_the_position_of_the_first_link_to_the_position_of_the_fourth_link(self):
        self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': self.fourth_link.position
            },
            format='json'
        )

        second_link_updated: Link = Link.objects.get(id=self.second_link.pk)
        third_link_updated: Link = Link.objects.get(id=self.third_link.pk)
        fourth_link_updated: Link = Link.objects.get(id=self.fourth_link.pk)

        self.assertEqual(second_link_updated.position, self.second_link.position - 1)
        self.assertEqual(third_link_updated.position, self.third_link.position - 1)
        self.assertEqual(fourth_link_updated.position, self.fourth_link.position - 1)

    def test_to_check_if_the_change_of_position_of_the_fourth_link_to_the_position_of_the_first_link_has_been_successful(self):
        self.client.post(
            self.url,
            {
                'link_id': self.fourth_link.pk,
                'new_position': self.first_link.position
            },
            format='json'
        )

        fourth_link_updated: Link = Link.objects.get(id=self.fourth_link.pk)

        self.assertEqual(fourth_link_updated.position, self.first_link.position)

    def test_to_check_if_the_links_are_arranged_correctly_after_changing_the_position_of_the_fourth_link_to_the_position_of_the_first_link(self):
        self.client.post(
            self.url,
            {
                'link_id': self.fourth_link.pk,
                'new_position': self.first_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)
        second_link_updated: Link = Link.objects.get(id=self.second_link.pk)
        third_link_updated: Link = Link.objects.get(id=self.third_link.pk)

        self.assertEqual(first_link_updated.position, self.first_link.position + 1)
        self.assertEqual(second_link_updated.position, self.second_link.position + 1)
        self.assertEqual(third_link_updated.position, self.third_link.position + 1)

    def test_to_check_if_the_links_are_arranged_correctly_after_changing_the_position_of_the_second_link_to_the_position_of_the_fourth_link(self):
        fifth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': self.second_link.pk,
                'new_position': self.fourth_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)
        third_link_updated: Link = Link.objects.get(id=self.third_link.pk)
        fourth_link_updated: Link = Link.objects.get(id=self.fourth_link.pk)
        fifth_link_updated: Link = Link.objects.get(id=fifth_link.pk)

        self.assertEqual(first_link_updated.position, self.first_link.position)
        self.assertEqual(third_link_updated.position, self.third_link.position - 1)
        self.assertEqual(fourth_link_updated.position, self.fourth_link.position - 1)
        self.assertEqual(fifth_link_updated.position, fifth_link.position)

    def test_to_return_error_response_and_status_code_401_if_a_channel_wants_to_change_position_a_link_that_is_not_their_own(self):
        not_own_link: Link = LinkFactory.create()

        response = self.client.post(
            self.url,
            {
                'link_id': not_own_link.pk,
                'new_position': self.first_link.pk
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'You do not own this link'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_and_status_code_404_if_the_link_does_not_exists(self):
        non_exists_first_link_id = self.first_link.pk

        self.first_link.delete()

        response = self.client.post(
            self.url,
            {
                'link_id': non_exists_first_link_id,
                'new_position': self.second_link.position
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link does not exists'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_404_if_no_link_exists_that_has_the_new_position(self):
        response = self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': 1000
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_error_response_and_status_code_400_if_the_new_position_is_equal_to_link_position(self):
        response = self.client.post(
            self.url,
            {
                'link_id': self.first_link.id,
                'new_position': self.first_link.position
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position must not be the same as the link position'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_link_id_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'link_id': faker.pystr(),
                'new_position': self.first_link.position
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The link ID must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_and_status_code_400_if_the_new_position_is_not_a_number(self):
        response = self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': faker.pystr()
            },
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position must be a number'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
