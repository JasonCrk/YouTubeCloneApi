from django.db.models import Q, Subquery, OuterRef, Sum, Count
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from apps.channel.models import Channel, ChannelSubscription
from apps.video.models import VideoView

from apps.channel.serializers import CreateChannelSerializer, UpdateChannelSerializer, ChannelSerializer, ChannelSimpleRepresentationSerializer

from youtube_clone.utils.storage import upload_image
from youtube_clone.enums import SortByEnum


class GetSubscribedChannelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        ids_channels_subscribed = ChannelSubscription.objects.filter(
            subscriber=request.user.current_channel
        ).values_list('subscribing__id', flat=True).order_by('subscription_date')

        channels_subscribed = Channel.objects.filter(id__in=ids_channels_subscribed)

        serialized_channels_subscribed = ChannelSimpleRepresentationSerializer(channels_subscribed, many=True)

        return Response({
            'data': serialized_channels_subscribed.data
        }, status=status.HTTP_200_OK)


class SearchChannelsView(APIView):
    def get(self, request, format=None):
        search_query = request.query_params.get('search_query')
        sort_by = request.query_params.get('sort_by')

        if not search_query:
            return Response({
                'message': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        filtered_channels = Channel.objects.filter(
            Q(name=search_query) | Q(name__icontains=search_query)
        )

        if sort_by == SortByEnum.UPLOAD_DATE.value:
            filtered_channels = filtered_channels.order_by('joined')
        elif sort_by == SortByEnum.VIEW_COUNT.value:
            total_video_views = Subquery(VideoView.objects.filter(video__channel__pk=OuterRef('pk')).values_list('count'))
            filtered_channels = filtered_channels.annotate(
                total_views=Sum(total_video_views)
            ).order_by('total_views')
        elif sort_by == SortByEnum.RATING.value:
            total_channel_subscribers = Subquery(ChannelSubscription.objects.filter(subscribing__pk=OuterRef('pk')).values_list('pk'))
            filtered_channels = filtered_channels.annotate(
                total_subscribers=Count(total_channel_subscribers)
            ).order_by('-total_subscribers')

        serialized_channels = ChannelSerializer(filtered_channels, many=True)

        return Response({
            'data': serialized_channels.data
        }, status=status.HTTP_200_OK)


class CreateChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        channel_data = request.data

        new_channel = CreateChannelSerializer(data={
            'name': channel_data['name'],
            'user': request.user.pk
        })

        if not new_channel.is_valid():
            return Response({
                'errors': new_channel.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if Channel.objects.filter(user=request.user).count() >= 10:
            return Response({
                'message': "You can't have more than 10 channels"
            }, status=status.HTTP_400_BAD_REQUEST)

        new_channel.save()

        return Response({
            'message': 'The channel has been created'
        }, status=status.HTTP_201_CREATED)


class SwitchChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            channel_id = int(request.data['channel_id'])
        except ValueError:
            return Response({
                'message': 'The channel ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel_to_change = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel_to_change.user != request.user:
            return Response({
                'message': 'You are not a owner of this channel'
            }, status=status.HTTP_401_UNAUTHORIZED)

        request.user.current_channel = channel_to_change
        request.user.save()

        return HttpResponse(status=status.HTTP_200_OK)


class SubscribeChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            channel_id = int(request.data['channel_id'])
        except:
            return Response({
                'message': 'The channel ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel == request.user.current_channel:
            return Response({
                'message': "Can't subscribe to itself"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel_subscription = ChannelSubscription.objects.get(
                subscriber=request.user.current_channel,
                subscribing=channel
            )

            channel_subscription.delete()

            return Response({
                'message': 'Subscription removed'
            }, status=status.HTTP_200_OK)
        except ChannelSubscription.DoesNotExist:
            channel.subscriptions.add(request.user.current_channel)

            return Response({
                'message': 'Subscription added'
            }, status=status.HTTP_200_OK)


class EditChannelView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def patch(self, request, format=None):
        channel_data = request.data.dict()

        if len(channel_data.keys()) == 0:
            return Response({
                'message': 'The data is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        updated_channel = UpdateChannelSerializer(
            request.user.current_channel,
            data=channel_data,
            partial=True
        )

        if not updated_channel.is_valid():
            return Response({
                'errors': updated_channel.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('banner') != None:
            try:
                banner_image_url = upload_image(channel_data.get('banner'), 'banners')
                updated_channel.validated_data['banner_url'] = banner_image_url
            except:
                return Response({
                    'message': 'Failed to upload channel banner, please try again later'
                }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('picture') != None:
            try:
                picture_image_url = upload_image(channel_data.get('picture'), 'pictures')
                updated_channel.validated_data['picture_url'] = picture_image_url
            except:
                return Response({
                    'message': 'Failed to upload channel picture, please try again later'
                }, status=status.HTTP_400_BAD_REQUEST)

        updated_channel.save()

        return Response({
            'message': 'The channel has been successfully updated'
        }, status=status.HTTP_200_OK)


class DeleteChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id, format=None):
        if Channel.objects.filter(user=request.user).count() < 2:
            return Response({
                'message': "You can't delete your last channel"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel.user != request.user:
            return Response({
                'message': 'You are not a owner of this channel'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if channel == request.user.current_channel:
            return Response({
                'message': 'Cannot delete a channel that is currently in use'
            }, status=status.HTTP_400_BAD_REQUEST)

        channel.delete()

        return Response({
            'message': 'The channel has been deleted'
        }, status=status.HTTP_200_OK)
