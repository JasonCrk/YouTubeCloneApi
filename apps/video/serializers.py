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


class ValidationVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField()
    thumbnail = serializers.FileField()

    class Meta:
        model = Video
        fields = (
            'title',
            'description',
            'video',
            'thumbnail'
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


class VideoLikeValidatorSerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField()

    class Meta:
        model = LikedVideo
        fields = (
            'liked',
            'video_id'
        )