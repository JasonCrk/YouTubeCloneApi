from rest_framework import serializers

from apps.channel.models import Channel, ChannelSubscription


class ChannelSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField('subscribers_count')

    def subscribers_count(self, instance: Channel):
        return ChannelSubscription.objects.filter(subscribing=instance).count()

    class Meta:
        model = Channel
        fields = (
            'id',
            'name',
            'handle',
            'picture_url',
            'subscribers'
        )

    def to_representation(self, instance: Channel):
        representation = super().to_representation(instance)

        representation['handle'] = '@'+instance.handle

        return representation


class ChannelSimpleRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'id',
            'picture_url',
            'name'
        )


class CreateChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'name',
            'user'
        )


class UpdateChannelSerializer(serializers.ModelSerializer):
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
