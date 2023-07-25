from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from tests.test_setup import TestSetup

from apps.channel.models import Channel

from faker import Faker

faker = Faker()


class TestEditChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.url = reverse('edit_channel')

    def test_to_return_success_response_if_channel_editing_has_been_successfully(self):
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

    def test_to_return_error_response_if_the_user_does_not_send_any_data(self):
        response = self.client.patch(
            self.url,
            data={},
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The data is required'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_check_if_the_channel_banner_has_been_edited_correctly(self):
        banner_content = faker.image(size=(16, 16), hue=[90, 270])

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

    def test_to_check_if_the_channel_picture_has_been_edited_correctly(self):
        picture_content = faker.image(size=(16, 16), hue=[90, 270])

        picture_image = SimpleUploadedFile('avatar_default.png', picture_content, content_type='image/png')

        self.client.patch(
            self.url,
            {
                'picture': picture_image
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(id=self.user.current_channel.pk)

        self.assertNotEqual(self.user.current_channel.picture_url, channel_edited.picture_url)

    def test_to_check_if_the_channel_description_has_been_edited_correctly(self):
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

    def test_to_check_if_the_channel_handle_has_been_edited_correctly(self):
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

    def test_to_check_if_the_channel_name_has_been_edited_correctly(self):
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

    def test_to_check_if_the_channel_contact_email_has_been_edited_correctly(self):
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

    def test_to_return_error_response_if_the_new_channel_name_exceeds_25_characters(self):
        response = self.client.patch(
            self.url,
            {
                'name': faker.pystr(min_chars=26, max_chars=27)
            },
            format='multipart'
        )

        self.assertIsNotNone(response.data.get('errors').get('name'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_new_channel_banner_is_not_a_image(self):
        fake_banner_content = faker.image(size=(2, 2), hue='purple', luminosity='bright', image_format='pdf')

        fake_banner = SimpleUploadedFile('faker_banner.pdf', fake_banner_content, content_type='application/pdf')

        response = self.client.patch(
            self.url,
            {
                'banner': fake_banner
            },
            format='multipart'
        )

        self.assertIsNotNone(response.data.get('errors').get('banner'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_new_channel_picture_is_not_a_image(self):
        fake_picture_content = faker.image(size=(2, 2), hue='purple', luminosity='bright', image_format='pdf')

        fake_picture = SimpleUploadedFile('faker_picture.pdf', fake_picture_content, content_type='application/pdf')

        response = self.client.patch(
            self.url,
            {
                'picture': fake_picture
            },
            format='multipart'
        )

        self.assertIsNotNone(response.data.get('errors').get('picture'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
