from rest_framework import serializers

from apps.playlist.models import Playlist, PlaylistVideo

from apps.video.serializers import FirstPlaylistVideoSerializer, VideoListSimpleSerializer
from apps.channel.serializers import ChannelSimpleRepresentationSerializer

from drf_spectacular.utils import extend_schema_field


class PlaylistDetailsSerializer(serializers.ModelSerializer):
    channel = ChannelSimpleRepresentationSerializer(read_only=True)
    first_video = serializers.SerializerMethodField('playlist_first_video')
    total_videos = serializers.SerializerMethodField('playlist_total_videos')

    @extend_schema_field(FirstPlaylistVideoSerializer)
    def playlist_first_video(self, instance: Playlist):
        if instance.video_thumbnail is None:
            return None

        return FirstPlaylistVideoSerializer(instance.video_thumbnail.video).data

    def playlist_total_videos(self, instance: Playlist) -> int:
        return PlaylistVideo.objects.filter(playlist=instance).count()

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'first_video',
            'channel',
            'description',
            'visibility',
            'total_videos',
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
    thumbnail = serializers.SerializerMethodField('selected_video_thumbnail')
    first_video_id = serializers.SerializerMethodField('playlist_first_video_id')
    number_videos = serializers.SerializerMethodField('playlist_number_videos')

    def selected_video_thumbnail(self, instance: Playlist) -> str:
        if instance.video_thumbnail is None:
            return None

        return instance.video_thumbnail.video.thumbnail

    def playlist_first_video_id(self, instance: Playlist) -> int:
        first_playlist_video = PlaylistVideo.objects.filter(playlist=instance).first()
        return first_playlist_video.video.pk if first_playlist_video is not None else None

    def playlist_number_videos(self, instance: Playlist) -> int:
        return PlaylistVideo.objects.filter(playlist=instance).count()

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'thumbnail',
            'first_video_id',
            'number_videos',
            'visibility',
            'updated_at',
        )


class PlaylistToSaveVideoSerializer(serializers.ModelSerializer):
    video_is_saved = serializers.SerializerMethodField('playlist_video_is_saved')

    def playlist_video_is_saved(self, instance: Playlist) -> bool:
        video_id = self.context.get('video_id')

        return PlaylistVideo.objects.filter(
            playlist=instance,
            video__pk=video_id
        ).exists()

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'visibility',
            'video_is_saved'
        )


class PlaylistListSimpleSerializer(serializers.ModelSerializer):
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
