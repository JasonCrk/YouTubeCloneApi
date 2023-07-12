from rest_framework import serializers

from apps.channel.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'banner',
            'picture',
            'description',
            'name',
            'handle',
        )