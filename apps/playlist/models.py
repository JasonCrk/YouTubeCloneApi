from typing import Dict, Tuple

from django.db import models

from apps.channel.models import Channel
from apps.video.models import Video

from apps.playlist.choices import Visibility


class Playlist(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    video_thumbnail = models.ForeignKey(
        "PlaylistVideo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='video_thumbnail'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    visibility = models.CharField(
        max_length=3,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self) -> str:
        return self.name


class PlaylistVideoManager(models.Manager):
    def create(self, video, playlist):
        last_playlist_video = self.get_queryset().filter(
            playlist=playlist
        ).last()

        if last_playlist_video is not None:
            position = last_playlist_video.position + 1
        else:
            position = 0

        return super().create(
            video=video,
            playlist=playlist,
            position=position
        )


class PlaylistVideo(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    objects = PlaylistVideoManager()

    def __str__(self) -> str:
        return self.video.title

    class Meta:
        ordering = ['position']

    def delete(self) -> Tuple[int, Dict[str, int]]:
        if self.playlist.video_thumbnail is not None and self.playlist.video_thumbnail.pk == self.pk:
            self.playlist.video_thumbnail = PlaylistVideo.objects.filter(
                playlist=self.playlist
            ).exclude(pk=self.pk).first()

            self.playlist.save()

        PlaylistVideo.objects.filter(
            playlist=self.playlist,
            position__gt=self.position
        ).update(
            position=models.F('position') - 1
        )

        return super(PlaylistVideo, self).delete()
