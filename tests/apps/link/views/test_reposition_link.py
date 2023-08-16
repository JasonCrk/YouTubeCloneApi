from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.link import LinkFactory

from apps.link.models import Link

from faker import Faker

faker = Faker()


class TestRepositionLink(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('reposition_link')

        self.first_link: Link = LinkFactory.create(channel=self.user.current_channel)
        self.second_link: Link = LinkFactory.create(channel=self.user.current_channel)

    def test_success_response(self):
        """
        Should return a success response if the link has been repositioned
        """
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

    def test_first_link_changes_position_with_the_second_link_position(self):
        """
        Should verify if the first link changes position with the second link position
        """
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

    def test_first_link_changes_position_with_the_fourth_link_position(self):
        """
        Should verify if the first link changes position with the fourth link position
        """
        LinkFactory.create(channel=self.user.current_channel)
        fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': fourth_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)

        self.assertEqual(first_link_updated.position, fourth_link.position)

    def test_arranged_after_changing_the_first_link_changes_position_with_the_fourth_link_position(self):
        """
        Should verify if the links arranged after changing the first link
        changes position with the fourth link position
        """
        third_link: Link = LinkFactory.create(channel=self.user.current_channel)
        fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': self.first_link.pk,
                'new_position': fourth_link.position
            },
            format='json'
        )

        second_link_updated: Link = Link.objects.get(id=self.second_link.pk)
        third_link_updated: Link = Link.objects.get(id=third_link.pk)
        fourth_link_updated: Link = Link.objects.get(id=fourth_link.pk)

        self.assertEqual(second_link_updated.position, self.second_link.position - 1)
        self.assertEqual(third_link_updated.position, third_link.position - 1)
        self.assertEqual(fourth_link_updated.position, fourth_link.position - 1)

    def test_fourth_link_changes_position_with_the_first_link_position(self):
        """
        Should verify if the fourth link changes position with the first link position
        """
        LinkFactory.create(channel=self.user.current_channel)
        fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': fourth_link.pk,
                'new_position': self.first_link.position
            },
            format='json'
        )

        fourth_link_updated: Link = Link.objects.get(id=fourth_link.pk)

        self.assertEqual(fourth_link_updated.position, self.first_link.position)

    def test_arranged_after_changing_the_fourth_link_changes_position_with_the_first_link_position(self):
        """
        Should verify if the links arranged after changing the fourth link
        changes position with the first link position
        """
        third_link: Link = LinkFactory.create(channel=self.user.current_channel)
        fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': fourth_link.pk,
                'new_position': self.first_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)
        second_link_updated: Link = Link.objects.get(id=self.second_link.pk)
        third_link_updated: Link = Link.objects.get(id=third_link.pk)

        self.assertEqual(first_link_updated.position, self.first_link.position + 1)
        self.assertEqual(second_link_updated.position, self.second_link.position + 1)
        self.assertEqual(third_link_updated.position, third_link.position + 1)

    def test_arranged_after_changing_the_second_link_changes_position_with_the_fifth_link_position(self):
        """
        Should verify if the links arranged after changing the second link
        changes position with the fifth link position
        """
        third_link: Link = LinkFactory.create(channel=self.user.current_channel)
        fourth_link: Link = LinkFactory.create(channel=self.user.current_channel)
        fifth_link: Link = LinkFactory.create(channel=self.user.current_channel)

        self.client.post(
            self.url,
            {
                'link_id': self.second_link.pk,
                'new_position': fourth_link.position
            },
            format='json'
        )

        first_link_updated: Link = Link.objects.get(id=self.first_link.pk)
        third_link_updated: Link = Link.objects.get(id=third_link.pk)
        fourth_link_updated: Link = Link.objects.get(id=fourth_link.pk)
        fifth_link_updated: Link = Link.objects.get(id=fifth_link.pk)

        self.assertEqual(first_link_updated.position, self.first_link.position)
        self.assertEqual(third_link_updated.position, third_link.position - 1)
        self.assertEqual(fourth_link_updated.position, fourth_link.position - 1)
        self.assertEqual(fifth_link_updated.position, fifth_link.position)

    def test_channel_wants_to_change_position_a_link_that_is_not_their_own(self):
        """
        Should return an error response if a channel wants to change position a link that is not their own
        """
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

    def test_link_does_not_exist(self):
        """
        Should return an error response if the link does not exist
        """
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

        self.assertDictEqual(response.data, {'message': 'The link does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_exist_the_link_that_has_the_new_position(self):
        """
        Should return an error response if no exist the link has the new position
        """
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

    def test_new_position_is_equal_to_link_position(self):
        """
        Should return an error response if the new position is equal to link position
        """
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

    def test_link_id_is_not_a_number(self):
        """
        Should return an error response if the link ID is not a number
        """
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

    def test_new_position_is_not_a_number(self):
        """
        Should return an error response if the new position is not a number
        """
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
