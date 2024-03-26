from rest_framework import serializers

from apps.playlist.models import Playlist, PlaylistVideo

from apps.video.serializers import VideoListSimpleSerializer
from apps.channel.serializers import ChannelSimpleRepresentationSerializer


class PlaylistDetailsSerializer(serializers.ModelSerializer):
    channel = ChannelSimpleRepresentationSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField('playlist_thumbnail')
    first_video_id = serializers.SerializerMethodField('playlist_first_video_id')
    total_videos = serializers.SerializerMethodField('playlist_total_videos')

    def playlist_first_video_id(self, instance: Playlist) -> int:
        try:
            return PlaylistVideo.objects.get(playlist=instance, position=0).video.pk
        except PlaylistVideo.DoesNotExist:
            return None

    def playlist_total_videos(self, instance: Playlist) -> int:
        return PlaylistVideo.objects.filter(playlist=instance).count()

    def playlist_thumbnail(self, instance: Playlist) -> str:
        if instance.video_thumbnail is not None:
            return instance.video_thumbnail.video.thumbnail 

        first_playlist_video = PlaylistVideo.objects.filter(playlist=instance, position=0).first()

        return first_playlist_video.video.thumbnail if first_playlist_video is not None else None

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'first_video_id',
            'thumbnail',
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
    thumbnail = serializers.SerializerMethodField('playlist_thumbnail')
    first_video_id = serializers.SerializerMethodField('playlist_first_video_id')
    total_videos = serializers.SerializerMethodField('playlist_total_videos')

    def playlist_thumbnail(self, instance: Playlist) -> str:
        if instance.video_thumbnail is not None:
            return instance.video_thumbnail.video.thumbnail 

        first_playlist_video = PlaylistVideo.objects.filter(playlist=instance, position=0).first()

        return first_playlist_video.video.thumbnail if first_playlist_video is not None else None

    def playlist_first_video_id(self, instance: Playlist) -> int:
        try:
            return PlaylistVideo.objects.get(playlist=instance, position=0).video.pk
        except PlaylistVideo.DoesNotExist:
            return None

    def playlist_total_videos(self, instance: Playlist) -> int:
        return PlaylistVideo.objects.filter(playlist=instance).count()

    class Meta:
        model = Playlist
        fields = (
            'id',
            'name',
            'thumbnail',
            'first_video_id',
            'total_videos',
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
