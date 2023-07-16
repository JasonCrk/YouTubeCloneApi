from django.db import models

from apps.user.models import Channel
from apps.video.models import Video


class Comment(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='comment_channel')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comment_video')
    comment = models.ForeignKey('self', on_delete=models.CASCADE, related_name='comment_comment', null=True, blank=True)
    content = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True, blank=True)
    was_edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(Channel, through='LikedComment', related_name='comment_likes')

    class Meta:
        ordering = ['publication_date']

    def __str__(self):
        return self.channel.name


class LikedComment(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return self.channel.name
