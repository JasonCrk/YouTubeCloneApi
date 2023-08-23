from rest_framework import serializers

from apps.playlist.models import Playlist, PlaylistVideo

from apps.video.serializers import VideoListSimpleSerializer


class PlaylistDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'description',
            'visibility',
            'created_at',
            'updated_at'
        )


class PlaylistVideoListSerializer(serializers.ModelSerializer):
    video = VideoListSimpleSerializer(read_only=True)

    class Meta:
        model = PlaylistVideo
        fields = (
            'id',
            'position',
            'video'
        )


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
