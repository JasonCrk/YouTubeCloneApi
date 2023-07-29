from rest_framework import serializers

from apps.video.models import Video, VideoView

from apps.channel.serializers import ChannelSimpleRepresentationSerializer


class VideoSerializer(serializers.ModelSerializer):
    channel = ChannelSimpleRepresentationSerializer(read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'video_url',
            'thumbnail',
            'description',
            'channel',
            'publication_date',
            'views',
            'likes',
        )

    def to_representation(self, instance: Video):
        representation = super().to_representation(instance)

        video_view_list_not_transformed = VideoView.objects.filter(video=instance).values_list('count')
        video_view_list_transformed = map(lambda view: view[0], video_view_list_not_transformed)
        total_video_views = sum(video_view_list_transformed)

        representation['views'] = total_video_views
        representation['likes'] = instance.likes.count()

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
    thumbnail = serializers.ImageField(required=False)
    title = serializers.CharField(max_length=45, required=False)

    class Meta:
        model = Video
        fields = (
            'title',
            'description',
            'thumbnail'
        )
