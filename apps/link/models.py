from django.db import models

from apps.channel.models import Channel


class Link(models.Model):
    position = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=15)
    url = models.URLField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
