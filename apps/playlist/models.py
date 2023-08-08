from django.db import models

from apps.channel.models import Channel
from apps.video.models import Video

from apps.playlist.choices import Visibility


class Playlist(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    thumbnail = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=150)
    description = models.TextField()
    visibility = models.CharField(
        max_length=3,
        choices=Visibility.choices,
        default=Visibility.PRIVATE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class PlaylistVideo(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.video.title
