from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from apps.video.models import Video, LikedVideo

from apps.video.serializers import CreateVideoSerializer, UpdateVideoValidatorSerializer

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


class LikeVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            video_id = int(request.data['video_id'])
        except ValueError:
            return Response({
                'message': 'The video ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            like_video = LikedVideo.objects.get(
                channel=request.user.current_channel,
                video=video
            )

            if like_video.liked:
                like_video.delete()

                return Response({
                    'message': 'Like video removed'
                }, status=status.HTTP_200_OK)

            like_video.liked = True
            like_video.save()
        except LikedVideo.DoesNotExist:
            LikedVideo.objects.create(
                channel=request.user.current_channel,
                video=video,
                liked=True
            ).save()

        return Response({
            'message': 'Like video added'
        }, status=status.HTTP_200_OK)


class DislikeVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            video_id = int(request.data['video_id'])
        except ValueError:
            return Response({
                'message': 'The video ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            dislike_video = LikedVideo.objects.get(
                channel=request.user.current_channel,
                video=video
            )

            if not dislike_video.liked:
                dislike_video.delete()

                return Response({
                    'message': 'Dislike video removed'
                }, status=status.HTTP_200_OK)

            dislike_video.liked = False
            dislike_video.save()
        except LikedVideo.DoesNotExist:
            LikedVideo.objects.create(
                channel=request.user.current_channel,
                video=video,
                liked=False
            ).save()

        return Response({
            'message': 'Dislike video added'
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