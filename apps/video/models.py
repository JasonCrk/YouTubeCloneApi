from django.db import models
from django.utils import timezone

from apps.channel.models import Channel


class Video(models.Model):
    title = models.CharField(max_length=45)
    video_url = models.URLField()
    thumbnail = models.URLField()
    description = models.TextField(null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    publication_date = models.DateTimeField(auto_now_add=True, blank=True)
    views = models.ManyToManyField(Channel, through='VideoView', related_name='video_views')
    likes = models.ManyToManyField(Channel, through='LikedVideo', related_name='video_likes')

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class VideoView(models.Model):
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_query_name='views',
        null=True,
        blank=True
    )
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    count = models.PositiveBigIntegerField(default=1)
    last_view_date = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        if self.channel is not None:
            return self.channel.name
        return self.video.title


class LikedVideo(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.channel.name
