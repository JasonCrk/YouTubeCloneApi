from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.playlist.serializers import CreatePlaylistSerializer


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
