from rest_framework import serializers

from drf_spectacular.utils import extend_schema_field

from apps.channel.models import Channel, ChannelSubscription
from apps.video.models import Video, VideoView
from apps.link.models import Link

from apps.link.serializers import LinkListSerializer


class ChannelDetailsSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField('channel_subscribers')
    links = serializers.SerializerMethodField('channel_links')
    total_videos = serializers.SerializerMethodField('channel_total_videos')
    total_views = serializers.SerializerMethodField('channel_total_views')
    subscribed = serializers.SerializerMethodField('channel_subscribed')

    def channel_subscribers(self, instance: Channel) -> int:
        return ChannelSubscription.objects.filter(subscribing=instance).count()

    @extend_schema_field(field=LinkListSerializer(many=True))
    def channel_links(self, instance: Channel):
        links = Link.objects.filter(channel=instance).order_by('position')
        return LinkListSerializer(links, many=True).data

    def channel_total_videos(self, instance: Channel) -> int:
        return Video.objects.filter(channel=instance).count()

    def channel_total_views(self, instance: Channel) -> int:
        list_video_views = VideoView.objects.filter(video__channel=instance).values_list('count', flat=True)
        return sum(list_video_views)

    def channel_subscribed(self, instance: Channel) -> int:
        request = self.context.get('request')

        if request == None: return False

        user = request.user

        if user is None or not user.is_authenticated: return False

        return ChannelSubscription.objects.filter(
            subscriber=user.current_channel,
            subscribing=instance
        ).exists()

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
            'links',
            'total_videos',
            'total_views',
            'subscribed',
        )

    def to_representation(self, instance: Channel):
        representation = super().to_representation(instance)
        representation['handle'] = '@'+instance.handle
        return representation


class ChannelListSerializer(serializers.ModelSerializer):
    subscribers = serializers.SerializerMethodField('subscribers_count')

    def subscribers_count(self, instance: Channel) -> int:
        return ChannelSubscription.objects.filter(subscribing=instance).count()

    class Meta:
        model = Channel
        fields = (
            'id',
            'name',
            'handle',
            'picture_url',
            'subscribers',
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
            'handle',
            'picture_url',
            'name',
        )

    def to_representation(self, instance: Channel):
        representation = super().to_representation(instance)

        representation['handle'] = '@'+instance.handle

        return representation


class CurrentChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'id',
            'picture_url',
            'name',
            'handle',
        )

    def to_representation(self, instance: Channel):
        representation = super().to_representation(instance)

        representation['handle'] = '@'+instance.handle

        return representation


class CreateChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = (
            'name',
            'user',
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
