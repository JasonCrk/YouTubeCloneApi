from django.test import TestCase

from tests.factories.link import LinkFactory

from apps.link.models import Link


class TestLinkModel(TestCase):
    def setUp(self):
        self.link: Link = LinkFactory.create()

    def test_str_of_the_link_model_is_the_link_title(self):
        """
        Should verify if the __str__() of the link model is the link title
        """
        self.assertEqual(self.link.__str__(), self.link.title)

    def test_default_order_by_position_from_least_to_greatest(self):
        """
        You should verify if when obtaining the links they are ordered by position from least to greatest
        """
        LinkFactory.create_batch(3, channel=self.link.channel)

        links = Link.objects.filter(channel=self.link.channel)

        for position, link in enumerate(links):
            self.assertEqual(link.position, position)

    def test_link_has_been_created(self):
        """
        Should verify if the link comment has been created
        """
        link = Link.objects.filter(id=self.link.pk)
        self.assertTrue(link.exists())

    def test_increase_in_position_of_a_created_link(self):
        """
        Should verify that the position of the created link is greater than all the links that the channel has
        """
        new_link: Link = LinkFactory.create(channel=self.link.channel)
        self.assertEqual(new_link.position, self.link.position + 1)

    def test_rearrangement_of_link_positions(self):
        """
        Should verify that the links are organized when a link is deleted
        """
        channel = self.link.channel

        LinkFactory.create_batch(2, channel=channel)

        self.link.delete()

        links = Link.objects.filter(channel=channel)

        for new_position, link in enumerate(links):
            self.assertEqual(link.position, new_position)
