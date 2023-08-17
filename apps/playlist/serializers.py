from rest_framework import serializers

from apps.playlist.models import Playlist


class PlaylistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
        )


class CreatePlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = (
            'name',
            'visibility',
            'channel',
        )


class UpdatePlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = (
            'name',
            'description',
            'visibility',
        )
