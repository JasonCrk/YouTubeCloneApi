from rest_framework import serializers

from apps.video.models import Video, VideoView, LikedVideo
from apps.comment.models import Comment
from apps.channel.models import ChannelSubscription

from apps.channel.serializers import ChannelSimpleRepresentationSerializer, ChannelListSerializer


class VideoListSimpleSerializer(serializers.ModelSerializer):
    channel = ChannelSimpleRepresentationSerializer(read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'thumbnail',
            'channel',
            'publication_date',
            'views',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        video_view_list = VideoView.objects.filter(video=instance).values_list('count', flat=True)
        total_video_views = sum(video_view_list)

        representation['views'] = total_video_views

        return representation


class VideoListSerializer(serializers.ModelSerializer):
    channel = ChannelSimpleRepresentationSerializer(read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'thumbnail',
            'description',
            'channel',
            'publication_date',
            'views',
            'likes',
        )

    def to_representation(self, instance: Video):
        representation = super().to_representation(instance)

        video_view_list = VideoView.objects.filter(video=instance).values_list('count', flat=True)
        total_video_views = sum(video_view_list)

        representation['views'] = total_video_views
        representation['likes'] = LikedVideo.objects.filter(video=instance, liked=True).count()

        return representation


class VideoDetailsSerializer(serializers.ModelSerializer):
    channel = ChannelListSerializer(read_only=True)
    dislikes = serializers.SerializerMethodField('video_dislikes')
    comments = serializers.SerializerMethodField('video_comments')
    liked = serializers.SerializerMethodField('video_liked')
    disliked = serializers.SerializerMethodField('video_disliked')

    def video_dislikes(self, instance: Video) -> int:
        return LikedVideo.objects.filter(video=instance, liked=False).count()

    def video_comments(self, instance: Video) -> int:
        return Comment.objects.filter(video=instance).count()

    def video_liked(self, instance: Video) -> bool:
        user = self.context['request'].user

        if not user.is_authenticated:
            return False

        return LikedVideo.objects.filter(
            video=instance,
            channel=user.current_channel,
            liked=True
        ).exists()

    def video_disliked(self, instance: Video) -> bool:
        user = self.context['request'].user

        if not user.is_authenticated:
            return False

        return LikedVideo.objects.filter(
            video=instance,
            channel=user.current_channel,
            liked=False
        ).exists()

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'video_url',
            'description',
            'channel',
            'publication_date',
            'views',
            'comments',
            'likes',
            'dislikes',
            'liked',
            'disliked',
        )

    def to_representation(self, instance: Video):
        representation = super().to_representation(instance)

        video_view_list = VideoView.objects.filter(video=instance).values_list('count', flat=True)
        total_video_views = sum(video_view_list)

        representation['views'] = total_video_views
        representation['likes'] = LikedVideo.objects.filter(video=instance, liked=True).count()

        user = self.context.get('request').user

        representation['channel']['subscribed'] = False

        if user != None and user.is_authenticated:
            representation['channel']['subscribed'] = ChannelSubscription.objects.filter(
                subscriber=user.current_channel,
                subscribing=instance.channel
            ).exists()

        return representation


class CreateVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField()
    thumbnail = serializers.ImageField()

    class Meta:
        model = Video
        fields = (
            'title',
            'description',
            'video',
            'thumbnail',
            'channel'
        )

    def create(self, validated_data):
        return Video.objects.create(
            title=validated_data['title'],
            description=validated_data.get('description'),
            video_url=validated_data.get('video_url'),
            thumbnail=validated_data.get('thumbnail'),
            channel=validated_data['channel']
        )


class UpdateVideoSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField()
    title = serializers.CharField(max_length=45)

    class Meta:
        model = Video
        fields = (
            'title',
            'description',
            'thumbnail'
        )
