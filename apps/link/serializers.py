from rest_framework import serializers

from apps.link.models import Link


class CreateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = (
            'title',
            'url',
            'channel'
        )
