from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from apps.channel.models import Channel

from faker import Faker

faker = Faker()


class TestEditChannel(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.url = reverse('edit_channel')

    def test_success_response(self):
        """
        Should return a success response if the channel has been updated
        """
        response = self.client.patch(
            self.url,
            {
                'description': faker.paragraph(),
                'title': faker.pystr(),
                'name': faker.user_name(),
                'handle': faker.pystr(max_chars=28),
                'contact_email': faker.email()
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The channel has been successfully updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_channel_banner_has_been_updated(self):
        """
        Should verify if the channel banner has been updated
        """
        banner_content = faker.image(size=(2, 2), hue=[90, 270])
        banner_image = SimpleUploadedFile('banner_default.png', banner_content, content_type='image/png')

        self.client.patch(
            self.url,
            {
                'banner': banner_image
            },
            format='multipart'
        )

        channel_edited: Channel = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertNotEqual(self.user.current_channel.banner_url, channel_edited.banner_url)

    def test_channel_picture_has_been_updated(self):
        """
        Should verify if the channel picture has been updated
        """
        picture_content = faker.image(size=(2, 2), hue=[90, 270])

        picture_image = SimpleUploadedFile('avatar_default.png', picture_content, content_type='image/png')

        self.client.patch(
            self.url,
            {
                'picture': picture_image
            },
            format='multipart'
        )

        channel_edited: Channel = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertNotEqual(self.user.current_channel.picture_url, channel_edited.picture_url)

    def test_channel_description_has_been_updated(self):
        """
        Should verify if the channel description has been updated
        """
        new_channel_description = faker.paragraph()

        self.client.patch(
            self.url,
            {
                'description': new_channel_description
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertEqual(new_channel_description, channel_edited.description)

    def test_channel_handle_has_been_updated(self):
        """
        Should verify if the channel handle has been updated
        """
        new_channel_handle = faker.pystr(max_chars=28)

        self.client.patch(
            self.url,
            {
                'handle': new_channel_handle
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertEqual(new_channel_handle, channel_edited.handle)

    def test_channel_name_has_been_updated(self):
        """
        Should verify if the channel name has been updated
        """
        new_channel_name = faker.user_name()

        self.client.patch(
            self.url,
            {
                'name': new_channel_name
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertEqual(new_channel_name, channel_edited.name)

    def test_channel_contact_email_has_been_updated(self):
        """
        Should verify if the channel contact email has been updated
        """
        new_channel_contact_email = faker.email()

        self.client.patch(
            self.url,
            {
                'contact_email': new_channel_contact_email
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertEqual(new_channel_contact_email, channel_edited.contact_email)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response if the data sent is invalid
        """
        response = self.client.patch(
            self.url,
            {
                'name': ''
            },
            format='multipart'
        )

        self.assertIsNotNone(response.data.get('errors').get('name'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
