from rest_framework import serializers

from apps.comment.models import Comment, LikedComment

from apps.channel.serializers import CurrentChannelSerializer


class CommentListSerializer(serializers.ModelSerializer):
    channel = CurrentChannelSerializer(read_only=True)
    dislikes = serializers.SerializerMethodField('comment_dislikes')
    liked = serializers.SerializerMethodField('comment_liked')
    disliked = serializers.SerializerMethodField('comment_disliked')
    comments = serializers.SerializerMethodField('comment_comments')

    def comment_dislikes(self, instance: Comment) -> int:
        return LikedComment.objects.filter(comment=instance, liked=False).count()

    def comment_liked(self, instance: Comment) -> bool:
        request = self.context.get('request')

        if request is None:
            return False

        user = request.user

        if not user.is_authenticated:
            return False

        return LikedComment.objects.filter(
            comment=instance,
            channel=user.current_channel,
            liked=True
        ).exists()

    def comment_disliked(self, instance: Comment) -> bool:
        request = self.context.get('request')

        if request is None:
            return False

        user = request.user

        if not user.is_authenticated:
            return False

        return LikedComment.objects.filter(
            comment=instance,
            channel=user.current_channel,
            liked=False
        ).exists()

    def comment_comments(self, instance: Comment) -> int:
        return Comment.objects.filter(
            comment=instance
        ).count()

    class Meta:
        model = Comment
        fields = (
            'id',
            'channel',
            'content',
            'publication_date',
            'was_edited',
            'likes',
            'dislikes',
            'liked',
            'disliked',
            'comments'
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
