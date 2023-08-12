from typing import Dict, Tuple
from django.db import models

from apps.channel.models import Channel


class LinkManager(models.Manager):
    def create(self, channel, title, url):
        last_channel_link = self.get_queryset().filter(
            channel=channel
        ).last()

        if last_channel_link is not None:
            position = last_channel_link.position + 1
        else:
            position = 0

        link = super().create(
            channel=channel,
            title=title,
            url=url,
            position=position
        )

        return link


class Link(models.Model):
    position = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=15)
    url = models.URLField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    objects = LinkManager()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.title

    def delete(self) -> Tuple[int, Dict[str, int]]:
        Link.objects.filter(
            channel=self.channel,
            position__gt=self.position
        ).update(
            position=models.F('position') - 1
        )

        return super(Link, self).delete()