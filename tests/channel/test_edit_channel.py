import os

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from tests.test_setup import TestSetup

from apps.channel.models import Channel
from apps.user.models import UserAccount


class TestEditChannel(TestSetup):
    def setUp(self):
        super().setUp()

        self.channel = Channel.objects.get(user=self.user)

        self.url = reverse('edit_channel', kwargs={'channel_id': self.channel.pk})

        self.banner_image_path = os.path.dirname(__file__) + '/images/banner_default.jpg'
        self.picture_image_path = os.path.dirname(__file__) + '/images/avatar_default.jpg'

    def test_to_return_an_error_response_if_the_user_does_not_update_any_attributes(self):
        response = self.client.patch(
            self.url,
            data={},
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'You need to update at least one attribute'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_return_an_error_response_if_the_user_wants_to_edit_a_channel_that_they_dont_own(self):
        test_user = UserAccount.objects.create_user(
            email='jaja@gmail.com',
            username='TestMen',
            first_name='Account2',
            last_name='Test2',
            password='AccountTestPassword2'
        )

        channel = Channel.objects.get(user__pk=test_user.pk)

        url = reverse('edit_channel', kwargs={'channel_id': channel.pk})

        response = self.client.patch(
            url,
            {
                'description': 'test description'
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this channel'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_success_response_if_channel_edit_successfully(self):
        response = self.client.patch(
            self.url,
            {
                'description': 'test description'
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The channel has been successfully updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_return_error_response_if_the_channel_does_not_exist(self):
        url = reverse('edit_channel', kwargs={'channel_id': 11})

        response = self.client.patch(
            url,
            {
                'description': 'test description'
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The channel does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_to_check_that_the_channel_banner_has_been_edited_correctly(self):
        with open(self.banner_image_path, 'rb') as file:
            file_content = file.read()

        banner_image = SimpleUploadedFile('banner_default.jpg', file_content, content_type='image/*')

        self.client.patch(
            self.url,
            {
                'banner': banner_image
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertNotEqual(channel_edited.banner_url, self.channel.banner_url)

    def test_to_check_that_the_channel_picture_has_been_edited_correctly(self):
        with open(self.picture_image_path, 'rb') as file:
            file_content = file.read()

        picture_image = SimpleUploadedFile('avatar_default.jpg', file_content, content_type='image/*')

        self.client.patch(
            self.url,
            {
                'picture': picture_image
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertNotEqual(channel_edited.picture_url, self.channel.picture_url)

    def test_to_check_that_the_channel_description_has_been_edited_correctly(self):
        new_channel_description = 'test description'

        self.client.patch(
            self.url,
            {
                'description': new_channel_description
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertEqual(new_channel_description, channel_edited.description)

    def test_to_check_that_the_channel_handle_has_been_edited_correctly(self):
        new_channel_handle = 'test_handle'

        self.client.patch(
            self.url,
            {
                'handle': new_channel_handle
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertEqual(new_channel_handle, channel_edited.handle)

    def test_to_check_that_the_channel_name_has_been_edited_correctly(self):
        new_channel_name = 'test name'

        self.client.patch(
            self.url,
            {
                'name': new_channel_name
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertEqual(new_channel_name, channel_edited.name)

    def test_to_check_that_the_channel_contact_email_has_been_edited_correctly(self):
        new_channel_contact_email = 'test_email@gmail.com'

        self.client.patch(
            self.url,
            {
                'contact_email': new_channel_contact_email
            },
            format='multipart'
        )

        channel_edited = Channel.objects.get(user=self.user)

        self.assertEqual(new_channel_contact_email, channel_edited.contact_email)

    def test_to_return_error_response_if_the_new_channel_name_exceeds_25_characters(self):
        response = self.client.patch(
            self.url,
            {
                'name': 'test name test name test name test name'
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('name'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_new_channel_banner_is_not_a_image(self):
        response = self.client.patch(
            self.url,
            {
                'banner': 'not an image'
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('banner'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_new_channel_picture_is_not_a_image(self):
        response = self.client.patch(
            self.url,
            {
                'picture': 'not an image'
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('picture'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
