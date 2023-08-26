from rest_framework import serializers

from apps.playlist.models import Playlist, PlaylistVideo

from apps.video.serializers import VideoListSimpleSerializer


class PlaylistDetailsSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField('selected_video_thumbnail')

    def selected_video_thumbnail(self, instance: Playlist):
        return instance.video_thumbnail.thumbnail if instance.video_thumbnail is not None else None

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'thumbnail',
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
            'video_thumbnail',
            'description',
            'visibility',
        )

    def update(self, instance, validated_data):
        if validated_data.get('video_thumbnail') is not None:
            if not PlaylistVideo.objects.filter(playlist=instance, pk=validated_data['video_thumbnail'].pk).exists():
                raise serializers.ValidationError(
                    'Video does not belong to the playlist'
                )

        return super().update(instance, validated_data)
