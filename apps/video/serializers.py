from rest_framework import serializers

from apps.video.models import Video, LikedVideo


class VideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=45, required=False)

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'video_url',
            'thumbnail',
            'description',
            'channel',
            'publication_date'
        )


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


class UpdateVideoValidatorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(required=False)
    title = serializers.CharField(max_length=45, required=False)

    class Meta:
        model = Video
        fields = (
            'title',
            'description',
            'thumbnail'
        )
