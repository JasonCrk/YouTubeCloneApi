from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.comment.models import Comment, LikedComment
from apps.video.models import Video

from apps.comment.serializers import CreateCommentSerializer, UpdateCommentSerializer


class CreateVideoCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id, format=None):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'the video does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        new_comment = CreateCommentSerializer(data={
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
            parent_comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The parent comment does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        new_comment = CreateCommentSerializer(data={
            'channel': request.user.current_channel.pk,
            'comment': parent_comment.pk,
            'video': parent_comment.video.pk,
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
                'message': 'The comment does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        like_comment = LikedComment.objects.filter(
            channel=request.user.current_channel,
            comment=comment
        ).first()

        if like_comment != None:
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


class EditCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, comment_id, format=None):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({
                'message': 'The comment does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.data.get('content') == comment.content:
            return Response({
                'message': 'The comment content has not been modified'
            }, status=status.HTTP_400_BAD_REQUEST)

        comment_updated = UpdateCommentSerializer(comment, data={'content': request.data['content']}, partial=True)

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
                'message': 'The comment does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        if comment.channel != request.user.current_channel:
            return Response({
                'message': 'You do not own this comment'
            }, status=status.HTTP_401_UNAUTHORIZED)

        comment.delete()

        return Response({
            'message': 'The comment has been deleted'
        }, status=status.HTTP_200_OK)
