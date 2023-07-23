from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.video.models import Video

from apps.comment.serializers import CreateCommentSerializer


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
