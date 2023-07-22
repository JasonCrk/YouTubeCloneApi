from rest_framework import serializers

from apps.channel.models import Channel


class CreateChannelValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'name',
            'user'
        )


class UpdateChannelValidationSerializer(serializers.ModelSerializer):
    banner = serializers.ImageField(required=False)
    picture = serializers.ImageField(required=False)
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
