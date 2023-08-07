from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status

from tests.test_setup import TestSetup

from tests.factories.video import VideoFactory
from tests.factories.user_account import UserFactory

from apps.video.models import Video
from apps.user.models import UserAccount

from faker import Faker

faker = Faker()


class TestEditVideo(TestSetup):
    def setUp(self):
        super().setUp()

        self.test_video = VideoFactory.create(channel=self.user.current_channel)

        self.url = reverse('edit_video', kwargs={'video_id': self.test_video.pk})

    def test_to_return_success_response_if_the_video_editing_has_been_successful(self):
        response = self.client.patch(
            self.url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_to_check_if_the_video_thumbnail_has_been_editing_successful(self):
        thumbnail_data = faker.image(size=(16, 16), hue=[90, 270], image_format='png')

        test_thumbnail = SimpleUploadedFile('thumbnail.png', thumbnail_data, content_type='image/png')

        self.client.patch(
            self.url,
            {
                'thumbnail': test_thumbnail
            },
            format='multipart'
        )

        test_video_updated = Video.objects.get(id=self.test_video.pk)

        self.assertNotEqual(self.test_video.thumbnail, test_video_updated.thumbnail)

    def test_to_check_if_the_video_title_has_been_editing_successful(self):
        self.client.patch(
            self.url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        test_video_updated = Video.objects.get(id=self.test_video.pk)

        self.assertNotEqual(self.test_video.title, test_video_updated.title)

    def test_to_check_if_the_video_description_has_been_editing_successful(self):
        self.client.patch(
            self.url,
            {
                'description': faker.paragraph()
            },
            format='multipart'
        )

        test_video_updated = Video.objects.get(id=self.test_video.pk)

        self.assertNotEqual(self.test_video.description, test_video_updated.description)

    def test_to_return_error_response_if_the_video_does_not_exist(self):
        url = reverse('edit_video', kwargs={'video_id': 1000})

        response = self.client.patch(
            url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exists'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_user_does_not_update_any_attributes(self):
        response = self.client.patch(
            self.url,
            {},
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'A minimum of 1 value is required to update the video'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_user_wants_to_update_a_video_that_he_does_not_own(self):
        test_user: UserAccount = UserFactory.create()

        not_own_video: Video = VideoFactory.create(channel=test_user.current_channel)

        url = reverse('edit_video', kwargs={'video_id': not_own_video.pk})

        response = self.client.patch(
            url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this video'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_to_return_error_response_if_the_video_thumbnail_is_not_a_image(self):
        fake_thumbnail_pdf_content = faker.image(size=(2, 2), hue='purple', luminosity='bright', image_format='pdf')

        fake_thumbnail = SimpleUploadedFile('fake_thumbnail.pdf', fake_thumbnail_pdf_content, content_type='application/pdf')

        response = self.client.patch(
            self.url,
            {
                'thumbnail': fake_thumbnail
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('thumbnail'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_to_return_error_response_if_the_video_title_exceeds_45_characters(self):
        response = self.client.patch(
            self.url,
            {
                'title': faker.pystr(min_chars=46, max_chars=47)
            },
            format='multipart'
        )

        self.assertNotEqual(response.data.get('errors').get('title'), None)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
