from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.playlist.models import Playlist, PlaylistVideo
from apps.video.models import Video
from apps.channel.models import Channel

from apps.playlist.serializers import CreatePlaylistSerializer, PlaylistListSerializer, PlaylistVideoListSerializer, UpdatePlaylistSerializer

from apps.playlist.choices import Visibility


class RetrieveVideosFromAPlaylist(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if playlist.visibility == Visibility.PRIVATE:
            if not request.user.is_authenticated or playlist.channel != request.user.current_channel:
                return Response({
                    'message': 'You are not authorized to view this playlist'
                }, status=status.HTTP_401_UNAUTHORIZED)

        playlist_videos = PlaylistVideo.objects.filter(playlist=playlist)

        serialized_playlist_videos = PlaylistVideoListSerializer(playlist_videos, many=True)

        return Response({
            'data': serialized_playlist_videos.data
        }, status=status.HTTP_200_OK)


class RetrieveChannelPlaylistsView(APIView):
    def get(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel_playlists = Playlist.objects.filter(
            channel=channel,
            visibility=Visibility.PUBLIC
        )

        serialized_channel_playlists = PlaylistListSerializer(channel_playlists, many=True)

        return Response({
            'data': serialized_channel_playlists.data
        }, status=status.HTTP_200_OK)


class RetrieveOwnPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        own_playlists = Playlist.objects.filter(channel=request.user.current_channel)

        serialized_own_playlists = PlaylistListSerializer(own_playlists, many=True)

        return Response({
            'data': serialized_own_playlists.data
        }, status=status.HTTP_200_OK)


class CreatePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data

        data['channel'] = request.user.current_channel.pk

        new_playlist = CreatePlaylistSerializer(data=data)

        if not new_playlist.is_valid():
            return Response({
                'errors': new_playlist.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_playlist_instance = new_playlist.save()

        serialized_playlist = PlaylistListSerializer(new_playlist_instance)

        return Response(serialized_playlist.data, status=status.HTTP_201_CREATED)


class SaveVideoToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if playlist.channel != request.user.current_channel:
            return Response({
                'message': 'You are not a owner of this playlist'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            video_id = int(request.data.get('video_id'))
        except (ValueError, TypeError):
            return Response({
                'message': 'The video ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if PlaylistVideo.objects.filter(playlist=playlist, video=video).exists():
            return Response({
                'message': 'The video is already in the playlist'
            }, status=status.HTTP_400_BAD_REQUEST)

        PlaylistVideo.objects.create(
            video=video,
            playlist=playlist
        ).save()

        playlist.updated_at = timezone.now()
        playlist.save()

        return Response({
            'message': f'Added to {playlist.name}'
        }, status=status.HTTP_201_CREATED)


class EditPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        playlist_updated = UpdatePlaylistSerializer(playlist, data=request.data, partial=True)

        if not playlist_updated.is_valid():
            return Response({
                'errors': playlist_updated.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if playlist.channel != request.user.current_channel:
            return Response({
                'message': 'You are not a owner of this playlist'
            }, status=status.HTTP_401_UNAUTHORIZED)

        playlist_updated.save()

        return Response({
            'message': 'Playlist updated'
        }, status=status.HTTP_200_OK)


class DeletePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.select_related('channel').get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if playlist.channel != request.user.current_channel:
            return Response({
                'message': 'You are not the owner of this playlist'
            }, status=status.HTTP_401_UNAUTHORIZED)

        playlist.delete()

        return Response({
            'message': 'The playlist has been deleted'
        }, status=status.HTTP_200_OK)


class RemoveVideoFromPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, playlist_video_id, format=None):
        try:
            playlist_video: PlaylistVideo = PlaylistVideo.objects\
                .select_related('playlist__channel')\
                .get(id=playlist_video_id)
        except PlaylistVideo.DoesNotExist:
            return Response({
                'message': 'The playlist video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if playlist_video.playlist.channel != request.user.current_channel:
            return Response({
                'message': "You can't remove a video from a playlist that you don't own"
            }, status=status.HTTP_401_UNAUTHORIZED)

        playlist_video.delete()

        playlist_video.playlist.updated_at = timezone.now()
        playlist_video.playlist.save()

        return Response({
            'message': f'Removed from {playlist_video.playlist.name}'
        }, status=status.HTTP_200_OK)
