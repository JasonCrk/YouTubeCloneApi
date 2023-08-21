from rest_framework import serializers

from apps.video.models import Video, VideoView, LikedVideo
from apps.comment.models import Comment

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
    comment_count = serializers.SerializerMethodField('video_comments')

    def video_dislikes(self, instance: Video):
        return LikedVideo.objects.filter(video=instance, liked=False).count()

    def video_comments(self, instance: Video):
        return Comment.objects.filter(video=instance).count()

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
            'likes',
            'dislikes',
            'comment_count'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        video_view_list = VideoView.objects.filter(video=instance).values_list('count', flat=True)
        total_video_views = sum(video_view_list)

        representation['views'] = total_video_views
        representation['likes'] = LikedVideo.objects.filter(video=instance, liked=True).count()

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
