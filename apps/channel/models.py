from django.db import models

from apps.user_profile.models import Profile

class Channel(models.Model):
    banner = models.URLField(verbose_name='Banner image URL', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    joined = models.DateTimeField(auto_now_add=True, blank=True)
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='channel_profile')
    handle = models.CharField(blank=True, unique=True)
    contact_email = models.EmailField(verbose_name='Contact email', null=True, blank=True)
    subscription = models.ManyToManyField(Profile, through='ChannelSubscription', related_name='channel_subscription')

    def __str__(self) -> str:
        return self.user_profile.user.username

class ChannelSubscription(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    subscription_date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self) -> str:
        return self.channel.handle
