from rest_framework import serializers

from apps.video.models import Video


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
