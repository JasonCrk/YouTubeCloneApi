from rest_framework import serializers

from apps.channel.models import Channel


class ChannelValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'banner_url',
            'picture_url',
            'description',
            'name',
            'handle',
        )


class UpdateChannelValidationSerializer(serializers.ModelSerializer):
    banner = serializers.FileField(required=False)
    picture = serializers.FileField(required=False)
    name = serializers.CharField(max_length=25, required=False)

    class Meta:
        model = Channel
        fields = (
            'handle',
            'description',
            'contact_email',
            'name',
            'banner',
            'picture',
        )


class CurrentChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'id',
            'picture_url',
            'name',
            'handle',
        )
