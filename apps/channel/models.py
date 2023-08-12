from django.db import models
from django.conf import settings

from .normalize_handle import normalize_handle

User = settings.AUTH_USER_MODEL


class ChannelManager(models.Manager):
    def create(self, name, user, **extra_fields):
        handle_normalize = normalize_handle(name)
        channel = super().create(
            handle=handle_normalize,
            name=name,
            user=user,
            **extra_fields
        )
        return channel


class Channel(models.Model):
    banner_url = models.URLField(verbose_name='Banner image URL', null=True, blank=True)
    picture_url = models.URLField(verbose_name='Avatar image URL', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='channel_user')
    name = models.CharField(verbose_name='channel name', max_length=25)
    handle = models.CharField(blank=True, unique=True, max_length=28)
    contact_email = models.EmailField(verbose_name='Contact email', null=True, blank=True)
    subscriptions = models.ManyToManyField('self', through='ChannelSubscription')

    objects = ChannelManager()

    def __str__(self):
        return self.name


class ChannelSubscription(models.Model):
    subscriber = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscriber')
    subscribing = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscribing')
    subscription_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.subscriber.name
