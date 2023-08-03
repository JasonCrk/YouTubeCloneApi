from rest_framework import serializers

from apps.link.models import Link


class LinkListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = (
            'id',
            'title',
            'url',
            'position'
        )


class CreateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = (
            'title',
            'url',
            'channel'
        )


class UpdateLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = (
            'title',
            'url'
        )
