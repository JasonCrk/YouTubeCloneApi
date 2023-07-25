from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from apps.video.models import Video, LikedVideo

from apps.video.serializers import CreateVideoSerializer, VideoLikeValidatorSerializer, UpdateVideoValidatorSerializer

from youtube_clone.utils.storage import upload_video, upload_image


class CreateVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, format=None):
        video_data = request.data.dict()

        new_video = CreateVideoSerializer(data={
            'video': video_data.get('video'),
            'thumbnail': video_data.get('thumbnail'),
            'title': video_data.get('title'),
            'description': video_data.get('description'),
            'channel': request.user.current_channel.pk
        })

        if not new_video.is_valid():
            return Response({
                'errors': new_video.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_video.validated_data['thumbnail'] = upload_image(video_data.get('thumbnail'), 'thumbnails')
        except:
            return Response({
                'message': 'Failed to upload video thumbnail, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_video.validated_data['video_url'] = upload_video(video_data.get('video'))
        except:
            return Response({
                'message': 'Failed to upload video, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        new_video.save()

        return Response({
            'message': 'The video has been uploaded successfully'
        }, status=status.HTTP_201_CREATED)


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
        except Video.DoesNotExist:
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


class EditVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def patch(self, request, video_id, format=None):
        data = request.data.dict()

        if len(data.keys()) == 0:
            return Response({
                'message': 'A minimum of 1 value is required to update the video'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        if video.channel != request.user.current_channel:
            return Response({
                'message': 'You are not a owner of this video'
            }, status=status.HTTP_401_UNAUTHORIZED)

        updated_video = UpdateVideoValidatorSerializer(video, data=data, partial=True)

        if not updated_video.is_valid():
            return Response({
                'errors': updated_video.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if data.get('thumbnail') != None:
            try:
                thumbnail_image_url = upload_image(data['thumbnail'], 'thumbnails')
                updated_video.validated_data['thumbnail'] = thumbnail_image_url
            except:
                return Response({
                    'message': 'Failed to upload video thumbnail, please try again later'
                }, status=status.HTTP_400_BAD_REQUEST)

        updated_video.save()

        return Response({
            'message': 'The video has been updated'
        }, status=status.HTTP_200_OK)


class DeleteVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, video_id, format=None):
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        if video.channel != request.user.current_channel:
            return Response({
                'message': 'You are not the owner of the video'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            video.delete()
        except:
            return Response({
                'message': 'Video deletion failed, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'The video has been deleted'
        }, status=status.HTTP_200_OK)