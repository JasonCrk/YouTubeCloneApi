from rest_framework import serializers

from apps.video.models import Video, LikedVideo


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


class VideoLikeValidatorSerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField()

    class Meta:
        model = LikedVideo
        fields = (
            'liked',
            'video_id'
        )