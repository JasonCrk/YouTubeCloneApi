from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from apps.video.models import Video, LikedVideo

from apps.video.serializers import ValidationVideoSerializer, VideoLikeValidatorSerializer

from youtube_clone.utils.storage import upload_video, upload_image


class CreateVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, format=None):
        video_data = request.data.dict()

        video_data_validation = ValidationVideoSerializer(data=video_data)

        if not video_data_validation.is_valid():
            return Response({
                'errors': video_data_validation.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            uploaded_thumbnail_url = upload_image(video_data.get('thumbnail'), 'thumbnails')
        except:
            return Response({
                'message': 'Failed to upload video thumbnail, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            uploaded_video_url = upload_video(video_data.get('video'))
        except:
            return Response({
                'message': 'Failed to upload video, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        Video.objects.create(
            video_url=uploaded_video_url,
            thumbnail=uploaded_thumbnail_url,
            title=video_data['title'],
            description=video_data['description'],
            channel=request.user.current_channel
        ).save()

        return Response({
            'message': 'The video has been uploaded successfully'
        }, status=status.HTTP_200_OK)


class LikeAndDislikeVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        video_like_data = request.data

        video_like_data_validation = VideoLikeValidatorSerializer(data=video_like_data)

        if not video_like_data_validation.is_valid():
            return Response({
                'errors': video_like_data_validation.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_like_data['video_id'])
        except ObjectDoesNotExist:
            return Response({
                'message': 'The video does not exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        find_video_like = LikedVideo.objects.filter(
            channel=request.user.current_channel,
            video=video
        )

        like_type = 'like' if video_like_data['liked'] else 'dislike'

        if not find_video_like.exists():
            like = LikedVideo.objects.create(
                channel=request.user.current_channel,
                video=video,
                liked=video_like_data['liked']
            )
            like.save()

            message = f'{like_type.capitalize()} video'

            return Response({
                'message': message
            }, status=status.HTTP_200_OK)

        video_like: LikedVideo = find_video_like.first()

        if video_like.liked != video_like_data['liked']:
            video_like.liked = video_like_data['liked']
            video_like.save()

            message = f'{like_type.capitalize()} video'

            return Response({
                'message': message
            }, status=status.HTTP_200_OK)

        video_like.delete()

        message = f'The {like_type} has been removed'

        return Response({
            'message': message
        }, status=status.HTTP_200_OK)
