from django.db.models import Count, Case, When, IntegerField

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse

from apps.comment.models import Comment, LikedComment
from apps.video.models import Video

from apps.comment import serializers

from youtube_clone.enums import CommentSortOptions


class RetrieveVideoCommentsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary='Retrieve video comments',
        description='Retrieve the comments of a video and these can be sorted by top comments and the newest first',
        responses={
            200: OpenApiResponse(
                description='Comments from a video',
                response=serializers.CommentListSerializer(many=True)
            ),
            404: OpenApiResponse(
                description='Video does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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
    @extend_schema(
        summary='Retrieve comments of comment',
        description='Get comments from a comment',
        responses={
            200: OpenApiResponse(
                description='Comments from a comment',
            ),
            404: OpenApiResponse(
                description='Comment does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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
    serializer_class = serializers.CreateCommentSerializer

    @extend_schema(
        summary='Create video comment',
        description='Channel can create a new comment from a video',
        request=inline_serializer(
            'CreateVideoComment',
            fields={
                'content': serializers.serializers.CharField()
            }
        ),
        responses={
            201: OpenApiResponse(
                description='Comment created successfully'
            ),
            404: OpenApiResponse(
                description='Video does not exist'
            ),
            400: OpenApiResponse(
                description='The data is invalid'
            )
        }
    )
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
    serializer_class = serializers.CreateCommentSerializer

    @extend_schema(
        summary='Create comment for a comment',
        description='A Channel can create a new comment from a comment',
        request=inline_serializer(
            'CreateCommentForComment',
            fields={
                'content': serializers.serializers.CharField()
            }
        ),
        responses={
            201: OpenApiResponse(
                description='Comment created successfully'
            ),
            404: OpenApiResponse(
                description='Comment does not exist'
            ),
            400: OpenApiResponse(
                description='The data is invalid'
            )
        }
    )
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
    serializer_class = serializers.LikedComment

    @extend_schema(
        summary='Like comment',
        description='A Channel can add and remove like of a comment',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Like added or removed',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Comment does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def post(self, request, comment_id, format=None):
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
    serializer_class = serializers.LikedComment

    @extend_schema(
        summary='Dislike comment',
        description='A Channel can add and remove dislike of a comment',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Dislike added or dislike removed',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Comment does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def post(self, request, comment_id, format=None):
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
    serializer_class = serializers.UpdateCommentSerializer

    @extend_schema(
        summary='Edit comment',
        description='A Channel can update a comment',
        responses={
            200: OpenApiResponse(
                description='Successful update',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Comment does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='The data is invalid',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def put(self, request, comment_id, format=None):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        comment_updated = serializers.UpdateCommentSerializer(
            comment,
            data={'content': request.data.get('content')},
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

    @extend_schema(
        summary='Delete comment',
        description='A Channel can delete a comment',
        responses={
            200: {'description': 'Comment deleted successfully'},
            404: {'description': 'Comment does not exist'},
            401: {'description': 'The comment is not yours'}
        }
    )
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
