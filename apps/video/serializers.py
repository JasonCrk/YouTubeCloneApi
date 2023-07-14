from rest_framework import serializers


class ValidationVideoSerializer(serializers.Serializer):
    video = serializers.FileField()
    thumbnail = serializers.FileField()
    title = serializers.CharField(max_length=45)
    description = serializers.CharField(allow_blank=True)
