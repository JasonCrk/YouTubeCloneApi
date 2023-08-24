import datetime

from django.db.models import Q, Count, Sum, Subquery, OuterRef
from django.http import Http404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from apps.video.models import Video, LikedVideo, VideoView

from apps.video import serializers

from youtube_clone.utils.storage import upload_video, upload_image

from youtube_clone.enums import SortByEnum, UploadDateEnum


class RetrieveVideoDetailsView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = serializers.VideoDetailsSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        return super().handle_exception(exc)


class SearchVideosView(APIView):
    def get(self, request, format=None):
        search_query = request.query_params.get('search_query')
        sort_by = request.query_params.get('sort_by')
        upload_date = request.query_params.get('upload_date')

        if not search_query:
            return Response({
                'message': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_videos = Video.objects.filter(
            Q(title=search_query) | Q(title__icontains=search_query)
        )

        # ESTO PODRÍA MEJORARLO
        if upload_date == UploadDateEnum.LAST_HOUR:
            filtered_videos = filtered_videos.filter(
                timestamp__hour=datetime.datetime.today().hour
            )
        elif upload_date == UploadDateEnum.TODAY:
            filtered_videos = filtered_videos.filter(
                publication_date__date=datetime.date.today()
            )
        elif upload_date == UploadDateEnum.THIS_WEEK:
            filtered_videos = filtered_videos.filter(
                publication_date__week=datetime.date.today().isocalendar().week
            )
        elif upload_date == UploadDateEnum.THIS_MONTH:
            filtered_videos = filtered_videos.filter(
                publication_date__month=datetime.datetime.today().month
            )
        elif upload_date == UploadDateEnum.THIS_YEAR:
            filtered_videos = filtered_videos.filter(
                publication_date__year=datetime.datetime.today().year
            )

        # ESTO PODRÍA MEJORARLO
        if sort_by == SortByEnum.UPLOAD_DATE.value:
            filtered_videos = filtered_videos.order_by('publication_date')
        elif sort_by == SortByEnum.VIEW_COUNT.value:
            total_video_views = Subquery(
                VideoView.objects.filter(
                    video__pk=OuterRef('pk')
                ).values_list('count')
            )
            filtered_videos = filtered_videos.annotate(
                total_views=Sum(total_video_views)
            ).order_by('total_views')
        elif sort_by == SortByEnum.RATING.value:
            filtered_videos = filtered_videos.annotate(
                num_likes=Count('likes')
            ).order_by('-num_likes')

        serialized_videos = serializers.VideoListSerializer(
            filtered_videos,
            many=True
        )

        return Response({
            'data': serialized_videos.data
        }, status=status.HTTP_200_OK)


class CreateVideoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def post(self, request, format=None):
        video_data = request.data.dict()

        video_data['channel'] = request.user.current_channel.pk

        new_video = serializers.CreateVideoSerializer(data=video_data)

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
            'message': 'The video has been uploaded'
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
                'message': 'The video does not exist'
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
                'message': 'The video does not exist'
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

        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

        if video.channel != request.user.current_channel:
            return Response({
                'message': 'You are not a owner of this video'
            }, status=status.HTTP_401_UNAUTHORIZED)

        updated_video = serializers.UpdateVideoSerializer(
            video,
            data=data,
            partial=True
        )

        if not updated_video.is_valid():
            return Response({
                'errors': updated_video.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if data.get('thumbnail') is not None:
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
                'message': 'The video does not exist'
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
