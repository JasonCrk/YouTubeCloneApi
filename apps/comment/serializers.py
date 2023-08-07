from rest_framework import serializers

from apps.comment.models import Comment, LikedComment

from apps.channel.serializers import CurrentChannelSerializer


class ListCommentSerializer(serializers.ModelSerializer):
    channel = CurrentChannelSerializer(read_only=True)
    dislikes = serializers.SerializerMethodField('comment_dislikes')

    def comment_dislikes(self, instance: Comment):
        return LikedComment.objects.filter(comment=instance, liked=False).count()

    class Meta:
        model = Comment
        fields = (
            'id',
            'channel',
            'content',
            'publication_date',
            'was_edited',
            'likes',
            'dislikes'
        )

    def to_representation(self, instance: Comment):
        representation = super().to_representation(instance)

        representation['likes'] = LikedComment.objects.filter(comment=instance, liked=True).count()

        return representation


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'channel',
            'video',
            'comment',
            'content',
        )


class UpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'content',
        )

    def update(self, instance, validated_data):
        validated_data['was_edited'] = True

        return super().update(instance, validated_data)
