from rest_framework import serializers

from apps.channel.models import Channel, ChannelSubscription
from apps.video.models import Video, VideoView


class ChannelDetailsSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField('channel_subscribers')
    total_videos = serializers.SerializerMethodField('channel_total_videos')
    total_views = serializers.SerializerMethodField('channel_total_views')

    def channel_subscribers(self, instance: Channel) -> int:
        return ChannelSubscription.objects.filter(subscribing=instance).count()

    def channel_total_videos(self, instance: Channel) -> int:
        return Video.objects.filter(channel=instance).count()

    def channel_total_views(self, instance: Channel) -> int:
        total_video_views = VideoView.objects.filter(video__channel__pk=instance.pk).values_list('count', flat=True)
        return sum(total_video_views)

    class Meta:
        model = Channel
        fields = (
            'id',
            'name',
            'handle',
            'description',
            'picture_url',
            'banner_url',
            'joined',
            'subscribers',
            'total_videos',
            'total_views',
        )

    def to_representation(self, instance: Channel):
        representation = super().to_representation(instance)
        representation['handle'] = '@'+instance.handle
        return representation


class ChannelListSerializer(serializers.ModelSerializer):
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
