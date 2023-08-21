from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status

from tests.setups import APITestCaseWithAuth

from tests.factories.video import VideoFactory

from apps.video.models import Video

from faker import Faker

faker = Faker()


class TestEditVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.video: Video = VideoFactory.create(channel=self.user.current_channel)

        self.url_name = 'edit_video'
        self.url = reverse(self.url_name, kwargs={'video_id': self.video.pk})

    def test_success_response(self):
        """
        Should return a success response if the video has been updated
        """
        response = self.client.patch(
            self.url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video has been updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_video_thumbnail_has_been_updated(self):
        """
        Should verify if the video thumbnail has been updated successfully
        """
        thumbnail_data = faker.image(size=(2, 2), hue=[90, 270], image_format='png')

        thumbnail = SimpleUploadedFile('thumbnail.png', thumbnail_data, content_type='image/png')

        self.client.patch(
            self.url,
            {
                'thumbnail': thumbnail
            },
            format='multipart'
        )

        video_updated = Video.objects.get(id=self.video.pk)

        self.assertNotEqual(self.video.thumbnail, video_updated.thumbnail)

    def test_video_title_has_been_updated(self):
        """
        Should verify if the video title has been updated successfully
        """
        self.client.patch(
            self.url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        video_updated = Video.objects.get(id=self.video.pk)

        self.assertNotEqual(self.video.title, video_updated.title)

    def test_video_description_has_been_updated(self):
        """
        Should verify if the video description has been updated
        """
        self.client.patch(
            self.url,
            {
                'description': faker.paragraph()
            },
            format='multipart'
        )

        video_updated = Video.objects.get(id=self.video.pk)

        self.assertNotEqual(self.video.description, video_updated.description)

    def test_video_does_not_exist(self):
        """
        Should return an error response and a 400 status code if the video does not exist
        """
        self.video.delete()

        response = self.client.patch(
            self.url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'The video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_another_channel_wants_to_edit_a_video_is_does_not_own(self):
        """
        Should return an error response and a 401 status code if another channel wants to edit a video is does not own
        """
        not_own_video: Video = VideoFactory.create()

        not_own_video_url = reverse(self.url_name, kwargs={'video_id': not_own_video.pk})

        response = self.client.patch(
            not_own_video_url,
            {
                'title': faker.pystr(max_chars=45)
            },
            format='multipart'
        )

        self.assertDictEqual(response.data, {'message': 'You are not a owner of this video'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_data_sent_is_invalid(self):
        """
        Should return an error response and a 400 status code if the data sent is invalid
        """
        fake_thumbnail_pdf_content = faker.image(
            size=(2, 2),
            hue='purple',
            luminosity='bright',
            image_format='pdf'
        )

        fake_thumbnail = SimpleUploadedFile(
            'fake_thumbnail.pdf',
            fake_thumbnail_pdf_content,
            content_type='application/pdf'
        )

        response = self.client.patch(
            self.url,
            {
                'title': faker.pystr(min_chars=46, max_chars=47),
                'thumbnail': fake_thumbnail
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('title', response.data.get('errors'))
        self.assertIn('thumbnail', response.data.get('errors'))
