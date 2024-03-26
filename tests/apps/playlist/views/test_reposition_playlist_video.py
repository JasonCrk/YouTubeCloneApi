from django.urls import reverse

from rest_framework import status

from tests.factories.playlist import PlaylistFactory, PlaylistVideoFactory
from tests.setups import APITestCaseWithAuth

from apps.playlist.models import Playlist, PlaylistVideo

from faker import Faker

faker = Faker()

class TestRepositionPlaylistVideo(APITestCaseWithAuth):
    def setUp(self):
        super().setUp()

        self.playlist: Playlist = PlaylistFactory.create(
            channel=self.user.current_channel,
            video_thumbnail=None
        )

        self.first_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)
        self.second_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        self.url_name = 'reposition_playlist_video'

    def test_success_response(self):
        """
        Should return a success response if the playlist video has been repositioned
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        response = self.client.post(
            url,
            {'new_position': self.second_playlist_video.position},
            format='json'
        )

        self.assertEqual(response.content, b'')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_first_playlist_video_changes_position_with_the_second_playlist_video_position(self):
        """
        Should verify if the first playlist video changes position with the second playlist video position
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        self.client.post(
            url,
            {
                'new_position': self.second_playlist_video.position
            },
            format='json'
        )

        first_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.first_playlist_video.pk)
        second_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.second_playlist_video.pk)

        self.assertEqual(self.first_playlist_video.position, second_playlist_video_updated.position)
        self.assertEqual(self.second_playlist_video.position, first_playlist_video_updated.position)

    def test_first_playlist_video_changes_position_with_the_fourth_playlist_video_position(self):
        """
        Should verify if the first playlist video changes position
        with the fourth playlist video position
        """
        PlaylistVideoFactory.create(playlist=self.playlist)
        fourth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        self.client.post(
            url,
            {'new_position': fourth_playlist_video.position},
            format='json'
        )

        first_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.first_playlist_video.pk)

        self.assertEqual(first_playlist_video_updated.position, fourth_playlist_video.position)

    def test_arranged_after_changing_the_first_playlist_video_changes_position_with_the_fourth_playlist_video_position(self):
        """
        Should verify if the playlist videos arranged after changing
        the first playlist video changes position with the fourth playlist video position
        """
        third_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)
        fourth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        self.client.post(
            url,
            {'new_position': fourth_playlist_video.position},
            format='json'
        )

        second_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.second_playlist_video.pk)
        third_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=third_playlist_video.pk)
        fourth_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=fourth_playlist_video.pk)

        self.assertEqual(
            second_playlist_video_updated.position,
            self.second_playlist_video.position - 1
        )
        self.assertEqual(
            third_playlist_video_updated.position,
            third_playlist_video.position - 1
        )
        self.assertEqual(
            fourth_playlist_video_updated.position,
            fourth_playlist_video.position - 1
        )

    def test_fourth_playlist_video_changes_position_with_the_first_playlist_video_position(self):
        """
        Should verify if the fourth playlist video
        changes position with the first playlist video position
        """
        PlaylistVideoFactory.create(playlist=self.playlist)
        fourth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': fourth_playlist_video.pk}
        )

        self.client.post(
            url,
            {'new_position': self.first_playlist_video.position},
            format='json'
        )

        fourth_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=fourth_playlist_video.pk)

        self.assertEqual(fourth_playlist_video_updated.position, self.first_playlist_video.position)

    def test_arranged_after_changing_the_fourth_playlist_video_changes_position_with_the_first_playlist_video_position(self):
        """
        Should verify if the playlist videos arranged after changing the fourth playlist video
        changes position with the first playlist video position
        """
        third_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)
        fourth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': fourth_playlist_video.pk}
        )

        self.client.post(
            url,
            {'new_position': self.first_playlist_video.position},
            format='json'
        )

        first_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.first_playlist_video.pk)
        second_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.second_playlist_video.pk)
        third_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=third_playlist_video.pk)
        fourth_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=fourth_playlist_video.pk)

        self.assertEqual(
            first_playlist_video_updated.position,
            self.first_playlist_video.position + 1
        )
        self.assertEqual(
            second_playlist_video_updated.position,
            self.second_playlist_video.position + 1
        )
        self.assertEqual(
            third_playlist_video_updated.position,
            third_playlist_video.position + 1
        )
        self.assertEqual(
            fourth_playlist_video_updated.position,
            self.first_playlist_video.position
        )

    def test_arranged_after_changing_the_second_playlist_video_changes_position_with_the_fifth_playlist_video_position(self):
        """
        Should verify if the playlist videos arranged after changing the second playlist video
        changes position with the fifth playlist video position
        """
        third_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)
        fourth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)
        fifth_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.second_playlist_video.pk}
        )

        self.client.post(
            url,
            {'new_position': fourth_playlist_video.position},
            format='json'
        )

        first_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=self.first_playlist_video.pk)
        third_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=third_playlist_video.pk)
        fourth_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=fourth_playlist_video.pk)
        fifth_playlist_video_updated: PlaylistVideo = PlaylistVideo.objects.get(id=fifth_playlist_video.pk)

        self.assertEqual(
            first_playlist_video_updated.position,
            self.first_playlist_video.position
        )
        self.assertEqual(
            third_playlist_video_updated.position,
            third_playlist_video.position - 1
        )
        self.assertEqual(
            fourth_playlist_video_updated.position,
            fourth_playlist_video.position - 1
        )
        self.assertEqual(
            fifth_playlist_video_updated.position,
            fifth_playlist_video.position
        )

    def test_playlist_is_not_yours(self):
        """
        Should return an error response if a channel wants to modify a playlist that is not theirs
        """
        not_own_playlist: Playlist = PlaylistFactory.create()

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': not_own_playlist.pk, 'playlist_video_id': self.second_playlist_video.pk}
        )

        response = self.client.post(
            url,
            {'new_position': self.first_playlist_video.pk},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist is not yours'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_playlist_does_not_exist(self):
        """
        Should return an error response if the playlist does not exist
        """
        non_exist_playlist_id = self.playlist.pk
        non_exist_first_playlist_video_id = self.first_playlist_video.pk

        self.playlist.delete()

        non_exist_playlist_url = reverse(
            self.url_name,
            kwargs={'playlist_id': non_exist_playlist_id, 'playlist_video_id': non_exist_first_playlist_video_id}
        )

        response = self.client.post(
            non_exist_playlist_url,
            {'new_position': 2},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_playlist_video_does_not_exist(self):
        """
        Should return an error response if the playlist video does not exist
        """
        non_exist_first_playlist_video_id = self.first_playlist_video.pk

        self.first_playlist_video.delete()

        non_exist_first_playlist_video_url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': non_exist_first_playlist_video_id}
        )

        response = self.client.post(
            non_exist_first_playlist_video_url,
            {'new_position': self.second_playlist_video.position},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The playlist video does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_exist_the_playlist_video_that_has_the_new_position(self):
        """
        Should return an error response if no exist the playlist video has the new position
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.pk}
        )

        response = self.client.post(
            url,
            {'new_position': 1000},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position does not exist'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_new_position_is_equal_to_playlist_video_position(self):
        """
        Should return an error response if the new position is equal to playlist video position
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.pk}
        )

        response = self.client.post(
            url,
            {'new_position': self.first_playlist_video.position},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position must not be the same as the playlist video position'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_position_is_not_a_number(self):
        """
        Should return an error response if the new position is not a number
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.pk}
        )

        response = self.client.post(
            url,
            {'new_position': faker.pystr()},
            format='json'
        )

        self.assertDictEqual(response.data, {'message': 'The new position must be a number'})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_update_video_thumbnail_of_playlist(self):
        """
        Should update the video thumbnail of playlist if the video thumbnail is null
        and the playlist video position is 0 or the new playlist video position is 0
        """
        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        self.client.post(
            url,
            {
                'new_position': self.second_playlist_video.position
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(pk=self.playlist.pk)
        first_playlist_video = PlaylistVideo.objects.get(position=0, playlist=self.playlist)

        self.assertEqual(playlist_updated.video_thumbnail.pk, first_playlist_video.pk)

    def test_dont_update_video_thumbnail_of_playlist_if_video_thumbnail_exist(self):
        """
        Shouldn't update the video thumbnail of playlist if the video thumbnail exist
        """
        self.playlist.video_thumbnail = self.first_playlist_video
        self.playlist.save()

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.first_playlist_video.id}
        )

        self.client.post(
            url,
            {
                'new_position': self.second_playlist_video.position
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(pk=self.playlist.pk)

        self.assertEqual(self.first_playlist_video.pk, playlist_updated.video_thumbnail.pk)

    def test_dont_update_video_thumbnail_of_playlist_if_playlist_video_position_or_new_playlist_video_position(self):
        """
        Shouldn't update the video thumbnail of playlist if the playlist video position is 0 or the new playlist video position is 0
        """
        third_playlist_video: PlaylistVideo = PlaylistVideoFactory.create(playlist=self.playlist)

        url = reverse(
            self.url_name,
            kwargs={'playlist_id': self.playlist.pk, 'playlist_video_id': self.second_playlist_video.id}
        )

        self.client.post(
            url,
            {
                'new_position': third_playlist_video.position
            },
            format='json'
        )

        playlist_updated = Playlist.objects.get(pk=self.playlist.pk)

        self.assertIsNone(playlist_updated.video_thumbnail)
