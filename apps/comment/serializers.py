from rest_framework import serializers

from apps.comment.models import Comment


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'channel',
            'video',
            'comment',
            'content',
        )
