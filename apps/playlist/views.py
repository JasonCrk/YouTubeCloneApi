from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.playlist.models import Playlist

from apps.playlist.serializers import CreatePlaylistSerializer, UpdatePlaylistSerializer


class CreatePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data

        data['channel'] = request.user.current_channel.pk

        playlist_created = CreatePlaylistSerializer(data=data)

        if not playlist_created.is_valid():
            return Response({
                'errors': playlist_created.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        playlist_created.save()

        return Response({
            'message': f'Added to {playlist_created.validated_data["name"]}'
        }, status=status.HTTP_201_CREATED)


class EditPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, playlist_id, format=None):
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({
                'message': 'The playlist does not exists'
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
