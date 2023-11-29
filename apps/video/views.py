from datetime import datetime

from django.db.models import Q, Count, Sum, Case, When, IntegerField

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.parsers import FormParser, MultiPartParser

from apps.video.models import Video, LikedVideo, VideoView
from apps.channel.models import Channel

from apps.video import serializers

from youtube_clone.utils.storage import CloudinaryUploader

from youtube_clone.enums import SearchSortOptions, SearchUploadDate, VideoSortOptions


class RetrieveChannelVideosView(APIView):
    def get(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(pk=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        sort_by = request.query_params.get('sort_by')

        channel_videos = Video.objects.filter(channel=channel)

        if sort_by == VideoSortOptions.MOST_POPULAR.value:
            channel_videos = channel_videos.annotate(
                total_views=Sum('videoview__count', default=0)
            ).order_by('-total_views')
        elif sort_by == VideoSortOptions.OLDEST_UPLOADED.value:
            channel_videos = channel_videos.order_by('-publication_date')
        elif sort_by == VideoSortOptions.RECENTLY_UPLOADED.value or sort_by is None:
            channel_videos = channel_videos.order_by('publication_date')

        serialized_channel_videos = serializers.VideoListSimpleSerializer(
            channel_videos,
            many=True
        )

        return Response({
            'data': serialized_channel_videos.data
        }, status=status.HTTP_200_OK)


class RetrieveVideoDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, video_id, format=None):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        serialized_video = serializers.VideoDetailsSerializer(
            video,
            context={'request': request}
        )

        return Response(
            serialized_video.data,
            status=status.HTTP_200_OK
        )


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

        if upload_date == SearchUploadDate.LAST_HOUR.value:
            filtered_videos = filtered_videos.filter(
                publication_date__hour=datetime.now().hour
            )
        elif upload_date == SearchUploadDate.TODAY.value:
            filtered_videos = filtered_videos.filter(
                publication_date__day=datetime.today().day
            )
        elif upload_date == SearchUploadDate.THIS_WEEK.value:
            filtered_videos = filtered_videos.filter(
                publication_date__week=datetime.today().isocalendar().week
            )
        elif upload_date == SearchUploadDate.THIS_MONTH.value:
            filtered_videos = filtered_videos.filter(
                publication_date__month=datetime.today().month
            )
        elif upload_date == SearchUploadDate.THIS_YEAR.value:
            filtered_videos = filtered_videos.filter(
                publication_date__year=datetime.today().year
            )

        if sort_by == SearchSortOptions.UPLOAD_DATE.value:
            filtered_videos = filtered_videos.order_by('publication_date')
        elif sort_by == SearchSortOptions.VIEW_COUNT.value:
            filtered_videos = filtered_videos.annotate(
                total_views=Sum('videoview__count', default=0)
            ).order_by('-total_views')
        elif sort_by == SearchSortOptions.RATING.value:
            filtered_videos = filtered_videos.annotate(
                num_likes=Count(
                    Case(
                        When(likedvideo__liked=True, then=1),
                        output_field=IntegerField()
                    )
                )
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
            new_video.validated_data['thumbnail'] = CloudinaryUploader.upload_image(video_data.get('thumbnail'), 'thumbnails')
        except:
            return Response({
                'message': 'Failed to upload video thumbnail, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_video.validated_data['video_url'] = CloudinaryUploader.upload_video(video_data.get('video'))
        except:
            return Response({
                'message': 'Failed to upload video, please try again later'
            }, status=status.HTTP_400_BAD_REQUEST)

        new_video.save()

        return Response({
            'message': 'The video has been uploaded'
        }, status=status.HTTP_201_CREATED)


class AddVisitToVideoView(APIView):
    def post(self, request, video_id, format=None):
        try:
            video = Video.objects.get(pk=video_id)
        except Video.DoesNotExist:
            return Response({
                'message': 'The video does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user.is_authenticated:
            video_view, created = VideoView.objects.get_or_create(
                channel=request.user.current_channel,
                video=video
            )

            if not created:
                video_view.count += 1
                video_view.save()
        else:
            video_view, created = VideoView.objects.get_or_create(
                channel=None,
                video=video
            )

            if not created:
                video_view.count += 1
                video_view.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeVideoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id, format=None):
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

    def post(self, request, video_id, format=None):
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
            }, status=status.HTTP_404_NOT_FOUND)

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
                thumbnail_image_url = CloudinaryUploader.upload_image(data['thumbnail'], 'thumbnails')
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

        video.delete()

        return Response({
            'message': 'The video has been deleted'
        }, status=status.HTTP_200_OK)
