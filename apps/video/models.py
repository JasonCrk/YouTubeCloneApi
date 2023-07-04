from django.db import models

from apps.channel.models import Channel

class Video(models.Model):
    title = models.CharField(max_length=45)
    video_url = models.URLField()
    description = models.TextField(null=True, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    publication_date = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title
