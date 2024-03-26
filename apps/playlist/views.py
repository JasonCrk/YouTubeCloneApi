from django.db.models import Count, F

from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse

from apps.playlist.models import Playlist, PlaylistVideo
from apps.video.models import Video
from apps.channel.models import Channel

from apps.playlist import serializers
from apps.playlist.choices import Visibility


class RetrieveOwnPlaylistsToSaveVideo(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Retrieve own playlists to save video',
        description='Get the own playlists to save video',
        responses={
            200: OpenApiResponse(
                response=serializers.PlaylistToSaveVideoSerializer
            ),
            404: OpenApiResponse(
                description='Video does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def get(self, request, video_id, format=None):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        created_playlists = Playlist.objects.filter(channel=request.user.current_channel)

        serialized_created_playlists = serializers.PlaylistToSaveVideoSerializer(
            created_playlists,
            many=True,
            context={'video_id': video.pk}
        )

        return Response({
            'data': serialized_created_playlists.data
        }, status=status.HTTP_200_OK)


class RetrievePlaylistDetailsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Retrieve playlist details',
        description='Get the details of a playlist by ID',
        responses={
            200: OpenApiResponse(
                response=serializers.PlaylistDetailsSerializer
            ),
            404: OpenApiResponse(
                description='Playlist does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description="You can't view this playlist, because the playlist is private",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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

        serialized_playlist = serializers.PlaylistDetailsSerializer(playlist)

        return Response(serialized_playlist.data, status=status.HTTP_200_OK)


class RetrieveVideosFromAPlaylistView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Retrieve playlist videos',
        description='Get the videos from a playlist',
        responses={
            200: OpenApiResponse(
                description='Videos from a playlist',
                response=serializers.PlaylistVideoListSerializer(many=True)
            ),
            404: OpenApiResponse(
                description='Playlist does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description="You can't view this playlist, because the playlist is private",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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

        serialized_playlist_videos = serializers.PlaylistVideoListSerializer(
            playlist_videos,
            many=True
        )

        return Response({
            'data': serialized_playlist_videos.data
        }, status=status.HTTP_200_OK)


class RetrieveChannelPlaylistsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Retrieve channel playlists',
        description='Get the playlists of a channel',
        responses={
            200: OpenApiResponse(
                description='Playlists from a channel',
                response=serializers.PlaylistListSerializer(many=True)
            ),
            404: OpenApiResponse(
                description='Channel does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
        }
    )
    def get(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel_playlists = Playlist.objects.filter(channel=channel)

        if request.user.is_authenticated and request.user.current_channel == channel:
            channel_playlists = channel_playlists.filter(
                playlistvideo__isnull=False
            ).annotate(
                video_count=Count('playlistvideo')
            )

            channel_playlists = channel_playlists.filter(video_count__gte=1)
        else:
            channel_playlists = Playlist.objects.filter(
                channel=channel,
                visibility=Visibility.PUBLIC
            )

        serialized_channel_playlists = serializers.PlaylistListSerializer(
            channel_playlists,
            many=True
        )

        return Response({
            'data': serialized_channel_playlists.data
        }, status=status.HTTP_200_OK)


class RetrieveOwnPlaylistsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Retrieve own playlists',
        description='Get the own playlists',
        responses={
            200: serializers.PlaylistListSimpleSerializer
        }
    )
    def get(self, request, format=None):
        own_playlists = Playlist.objects.filter(channel=request.user.current_channel)

        serialized_own_playlists = serializers.PlaylistListSimpleSerializer(
            own_playlists,
            many=True
        )

        return Response({
            'data': serialized_own_playlists.data
        }, status=status.HTTP_200_OK)


class CreatePlaylistView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreatePlaylistSerializer

    @extend_schema(
        summary='Create playlist',
        description='Create a new playlist',
        request=inline_serializer(
            'CreatePlaylist',
            fields={
                'name': serializers.serializers.CharField(),
                'visibility': serializers.serializers.ChoiceField(choices=Visibility.choices)
            }
        ),
        responses={
            201: serializers.PlaylistListSimpleSerializer,
            400: OpenApiResponse(
                description='The data is invalid',
                response={
                    'type': 'object',
                    'properties': {
                        'errors': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'array', 'items': {'type': 'string'}},
                                'visibility': {'type': 'array', 'items': {'type': 'string'}},
                            }
                        }
                    }
                }
            )
        }
    )
    def post(self, request, format=None):
        data = request.data
        data['channel'] = request.user.current_channel.pk

        new_playlist = serializers.CreatePlaylistSerializer(data=data)

        if not new_playlist.is_valid():
            return Response({
                'errors': new_playlist.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_playlist_instance = new_playlist.save()

        serialized_playlist = serializers.PlaylistListSimpleSerializer(
            new_playlist_instance
        )

        return Response(serialized_playlist.data, status=status.HTTP_201_CREATED)


class SaveVideoToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PlaylistListSimpleSerializer

    @extend_schema(
        summary='Save video to playlist',
        description='Save a video to a playlist',
        request=inline_serializer(
            'SaveVideoToPlaylist',
            fields={
                'video_id': serializers.serializers.IntegerField()
            }
        ),
        responses={
            201: OpenApiResponse(
                description='Video saved successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Playlist or video does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='The playlist is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Video ID is not a number or the video is already in the playlist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
        }
    )
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
        except:
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

        new_playlist_video = PlaylistVideo.objects.create(
            video=video,
            playlist=playlist
        )
        new_playlist_video.save()

        playlist.updated_at = timezone.now()
        playlist.save()

        return Response({
            'message': f'Added to {playlist.name}'
        }, status=status.HTTP_201_CREATED)


class RepositionPlaylistVideoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Reposition playlist video',
        description='Reposition playlist video',
        request=inline_serializer(
            'RepositionPlaylistVideo',
            fields={
                'new_position': serializers.serializers.IntegerField()
            }
        ),
        responses={
            204: OpenApiResponse(
                description='Playlist video successfully repositioned',
            ),
            400: OpenApiResponse(
                description='The new position is not a number',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='The playlist or playlist video does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='The playlist or playlist video is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
        }
    )
    def post(self, request, playlist_id, playlist_video_id, format=None):
        try:
            new_playlist_video_position = int(request.data.get('new_position'))
        except:
            return Response({
                'message': 'The new position must be a number'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        try:
            playlist = Playlist.objects.get(pk=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        current_channel = request.user.current_channel

        if playlist.channel != current_channel:
            return Response({
                'message': 'The playlist is not yours'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            playlist_video = PlaylistVideo.objects.get(pk=playlist_video_id, playlist=playlist)
        except PlaylistVideo.DoesNotExist:
            return Response({
                'message': 'The playlist video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if playlist_video.position == new_playlist_video_position:
            return Response({
                'message': 'The new position must not be the same as the playlist video position'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            playlist_video_to_update: PlaylistVideo = PlaylistVideo.objects.get(
                playlist=playlist,
                position=new_playlist_video_position
            )
        except PlaylistVideo.DoesNotExist:
            return Response({
                'message': 'The new position does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        playlist_videos_rearrange = PlaylistVideo.objects.filter(
            playlist=playlist
        ).exclude(pk=playlist_video.pk)

        if abs(playlist_video.position - new_playlist_video_position) == 1:
            playlist_video_to_update.position = playlist_video.position
            playlist_video_to_update.save()
        elif playlist_video.position > new_playlist_video_position:
            playlist_videos_rearrange = playlist_videos_rearrange.filter(
                position__range=(new_playlist_video_position, playlist_video.position)
            )
            playlist_videos_rearrange.update(position=F('position') + 1)
        else:
            playlist_videos_rearrange = playlist_videos_rearrange.filter(
                position__range=(playlist_video.position, new_playlist_video_position)
            )
            playlist_videos_rearrange.update(position=F('position') - 1)

        old_playlist_video_position = playlist_video.position

        playlist_video.position = new_playlist_video_position
        playlist_video.save()

        if playlist.video_thumbnail is None and (old_playlist_video_position == 0 or new_playlist_video_position == 0):
            playlist.video_thumbnail = PlaylistVideo.objects.get(
                playlist=playlist,
                position=0
            )
            playlist.save()

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


class EditPlaylistView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdatePlaylistSerializer

    @extend_schema(
        summary='Edit playlist',
        description='Edit a playlist',
        responses={
            200: OpenApiResponse(
                description='Playlist updated successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Playlist does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='The data is invalid',
                response={
                    'type': 'object',
                    'properties': {
                        'errors': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'array', 'items': {'type': 'string'}},
                                'visibility': {'type': 'array', 'items': {'type': 'string'}},
                                'video_thumbnail': {'type': 'array', 'items': {'type': 'string'}},
                                'description': {'type': 'array', 'items': {'type': 'string'}},
                            }
                        }
                    }
                }
            ),
            401: OpenApiResponse(
                description='Playlist is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def patch(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        playlist_updated = serializers.UpdatePlaylistSerializer(
            playlist,
            data=request.data,
            partial=True
        )

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

    @extend_schema(
        summary='Delete playlist',
        description='Delete a playlist',
        responses={
            200: OpenApiResponse(
                description='Playlist deleted successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Playlist does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='Playlist is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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

    @extend_schema(
        summary='Remove video from playlist',
        description='Remove a video from a playlist',
        responses={
            200: OpenApiResponse(
                description='Video removed successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Playlist video does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='Playlist is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def delete(self, request, playlist_id, video_id, format=None):
        try:
            playlist_video: PlaylistVideo = PlaylistVideo.objects\
                .select_related('playlist__channel')\
                .get(video__pk=video_id, playlist__pk=playlist_id)
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
