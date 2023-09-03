from django.db.models import Count, Case, When, IntegerField

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from apps.comment.models import Comment, LikedComment
from apps.video.models import Video

from apps.comment import serializers

from youtube_clone.enums import CommentSortOptions


class RetrieveVideoCommentsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, video_id, format=None):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        sort_by = request.query_params.get('sort_by')

        video_comments = Comment.objects.filter(video=video, comment__isnull=True)

        if sort_by == CommentSortOptions.TOP_COMMENTS.value:
            video_comments = video_comments.annotate(
                num_likes=Count(
                    Case(
                        When(likedcomment__liked=True, then=1),
                        output_field=IntegerField()
                    )
                )
            ).order_by('-num_likes')
        elif sort_by == CommentSortOptions.NEWEST_FIRST.value:
            video_comments = video_comments.order_by('publication_date')

        serialized_video_comments = serializers.CommentListSerializer(
            video_comments,
            many=True,
            context={'request': request}
        )

        return Response({
            'data': serialized_video_comments.data
        }, status=status.HTTP_200_OK)


class RetrieveCommentsOfCommentView(APIView):
    def get(self, request, comment_id, format=None):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        comments_of_comment = Comment.objects.filter(comment=comment)

        serialized_comments_of_comment = serializers.CommentListSerializer(
            comments_of_comment,
            many=True,
            context={'request': request}
        )

        return Response({
            'data': serialized_comments_of_comment.data
        }, status=status.HTTP_200_OK)


class CreateVideoCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id, format=None):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'the video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        new_comment = serializers.CreateCommentSerializer(data={
            'channel': request.user.current_channel.pk,
            'video': video.pk,
            'content': request.data.get('content')
        })

        if not new_comment.is_valid():
            return Response({
                'errors': new_comment.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_comment.save()

        return Response({
            'message': 'The comment has been created'
        }, status=status.HTTP_201_CREATED)


class CreateCommentForCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        try:
            comment_parent = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment parent does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['channel'] = request.user.current_channel.pk
        data['comment'] = comment_parent.pk
        data['video'] = comment_parent.video.pk

        new_comment = serializers.CreateCommentSerializer(data=data)

        if not new_comment.is_valid():
            return Response({
                'errors': new_comment.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_comment.save()

        return Response({
            'message': 'The comment has been created'
        }, status=status.HTTP_201_CREATED)


class LikeCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            comment_id = int(request.data['comment_id'])
        except ValueError:
            return Response({
                'message': 'The comment ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        like_comment = LikedComment.objects.filter(
            channel=request.user.current_channel,
            comment=comment
        ).first()

        if like_comment is not None:
            if like_comment.liked:
                like_comment.delete()

                return Response({
                    'message': 'Like comment removed'
                }, status=status.HTTP_200_OK)

            like_comment.liked = True
            like_comment.save()
        else:
            LikedComment.objects.create(
                channel=request.user.current_channel,
                comment=comment,
                liked=True
            ).save()

        return Response({
            'message': 'Like comment added'
        }, status=status.HTTP_200_OK)


class DislikeCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            comment_id = int(request.data['comment_id'])
        except ValueError:
            return Response({
                'message': 'The comment ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        dislike_comment = LikedComment.objects.filter(
            channel=request.user.current_channel,
            comment=comment
        ).first()

        if dislike_comment is not None:
            if dislike_comment.liked == False:
                dislike_comment.delete()

                return Response({
                    'message': 'Dislike comment removed'
                }, status=status.HTTP_200_OK)

            dislike_comment.liked = False
            dislike_comment.save()
        else:
            LikedComment.objects.create(
                channel=request.user.current_channel,
                comment=comment,
                liked=False
            ).save()

        return Response({
            'message': 'Dislike comment added'
        }, status=status.HTTP_200_OK)


class EditCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id, format=None):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        comment_updated = serializers.UpdateCommentSerializer(
            comment,
            data={'content': request.data['content']},
            partial=True
        )

        if not comment_updated.is_valid():
            return Response({
                'errors': comment_updated.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        comment_updated.save()

        return Response({
            'message': 'The comment has been updated'
        }, status=status.HTTP_200_OK)


class DeleteCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id, format=None):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if comment.channel != request.user.current_channel:
            return Response({
                'message': 'You do not own this comment'
            }, status=status.HTTP_401_UNAUTHORIZED)

        comment.delete()

        return Response({
            'message': 'The comment has been deleted'
        }, status=status.HTTP_200_OK)
