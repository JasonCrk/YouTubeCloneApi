from django.db.models import Q, Subquery, OuterRef, Sum, Count
from django.http import HttpResponse, Http404

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse

from apps.channel.models import Channel, ChannelSubscription
from apps.video.models import VideoView

from apps.channel import serializers

from youtube_clone.utils.storage import CloudinaryUploader
from youtube_clone.enums import SearchSortOptions


class RetrieveChannelDetailsByIdView(generics.RetrieveAPIView):
    queryset = Channel.objects.all()
    serializer_class = serializers.ChannelDetailsSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response({
                'message': 'The channel does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        return super().handle_exception(exc)


class RetrieveChannelDetailsByHandleView(APIView):
    @extend_schema(
        summary='Retrieve channel details by handle',
        description='Get the detail of a channel by its handle',
        responses={
            200: OpenApiResponse(
                response=serializers.ChannelDetailsSerializer
            ),
            404: OpenApiResponse(
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def get(self, request, channel_handle, format=None):
        try:
            channel = Channel.objects.get(handle=channel_handle)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exists'
            }, status=status.HTTP_404_NOT_FOUND)

        serialized_channel = serializers.ChannelDetailsSerializer(channel)

        return Response(serialized_channel.data, status=status.HTTP_200_OK)


class RetrieveSubscribedChannelsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Retrieve subscribed channels',
        description='',
        responses={
            200: OpenApiResponse(
                response=serializers.ChannelSimpleRepresentationSerializer(many=True)
            )
        }
    )
    def get(self, request, format=None):
        ids_channels_subscribed = ChannelSubscription.objects.filter(
            subscriber=request.user.current_channel
        ).values_list('subscribing__id', flat=True).order_by('subscription_date')

        channels_subscribed = Channel.objects.filter(id__in=ids_channels_subscribed)

        serialized_channels_subscribed = serializers.ChannelSimpleRepresentationSerializer(
            channels_subscribed,
            many=True
        )

        return Response({
            'data': serialized_channels_subscribed.data
        }, status=status.HTTP_200_OK)


class SearchChannelsView(APIView):
    @extend_schema(
        summary='Search channels',
        description='',
        responses={
            200: OpenApiResponse(
                response=serializers.ChannelListSerializer(many=True)
            ),
            400: OpenApiResponse(
                description='Search query is required',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
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

        if sort_by == SearchSortOptions.UPLOAD_DATE.value:
            filtered_channels = filtered_channels.order_by('joined')
        elif sort_by == SearchSortOptions.VIEW_COUNT.value:
            total_video_views = Subquery(
                VideoView.objects.filter(
                    video__channel__pk=OuterRef('pk')
                ).values_list('count')
            )

            filtered_channels = filtered_channels.annotate(
                total_views=Sum(total_video_views)
            ).order_by('total_views')
        elif sort_by == SearchSortOptions.RATING.value:
            total_channel_subscribers = Subquery(
                ChannelSubscription.objects.filter(
                    subscribing__pk=OuterRef('pk')
                ).values_list('pk')
            )

            filtered_channels = filtered_channels.annotate(
                total_subscribers=Count(total_channel_subscribers)
            ).order_by('-total_subscribers')

        serialized_channels = serializers.ChannelListSerializer(
            filtered_channels,
            many=True
        )

        return Response({
            'data': serialized_channels.data
        }, status=status.HTTP_200_OK)


class CreateChannelView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateChannelSerializer

    @extend_schema(
        summary='Create channel',
        description='Create a channel',
        request=inline_serializer(
            'CreateChannel',
            fields={
                'name': serializers.serializers.CharField()
            }
        ),
        responses={
            200: OpenApiResponse(
                description='Channel has been created successfully',
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
                        'errors': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        }
                    }
                }
            ),
        }
    )
    def post(self, request, format=None):
        channel_data = request.data

        channel_data['user'] = request.user.pk

        new_channel = serializers.CreateChannelSerializer(data=channel_data)

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
    serializer_class = serializers.CurrentChannelSerializer

    @extend_schema(
        summary='Switch channel',
        description='Switch to another channel that you own',
        request=None,
        responses={
            204: OpenApiResponse(
                description='Channel change successful'
            ),
            404: OpenApiResponse(
                description='Channel does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='You are not the owner of this channel',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def post(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(pk=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel.user != request.user:
            return Response({
                'message': 'You are not a owner of this channel'
            }, status=status.HTTP_401_UNAUTHORIZED)

        request.user.current_channel = channel
        request.user.save()

        return HttpResponse(status=status.HTTP_204_NO_CONTENT)


class SubscribeChannelView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdateChannelSerializer

    @extend_schema(
        summary='Subscribe channel',
        description='A channel subscribes to another channel and remove the subscription',
        request=None,
        responses={
            200: OpenApiResponse(
                description='Channel subscribe to channel or remove channel subscription successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Channel does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Channel cannot subscribe to itself',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        },
    )
    def post(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(pk=channel_id)
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
            ChannelSubscription.objects.create(
                subscriber=request.user.current_channel,
                subscribing=channel
            ).save()

            return Response({
                'message': 'Subscription added'
            }, status=status.HTTP_200_OK)


class EditChannelView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]
    serializer_class = serializers.UpdateChannelSerializer

    @extend_schema(
        summary='Edit channel',
        description='User can edit their current channel',
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
            400: OpenApiResponse(
                description='Data is invalid',
                response={
                    'type': 'object',
                    'properties': {
                        'errors': {
                            'type': 'object',
                            'properties': {
                                'handle': {'type': 'array', 'items': {'type': 'string'}},
                                'description': {'type': 'array', 'items': {'type': 'string'}},
                                'contact_email': {'type': 'array', 'items': {'type': 'string'}},
                                'name': {'type': 'array', 'items': {'type': 'string'}},
                                'banner': {'type': 'array', 'items': {'type': 'string'}},
                                'picture': {'type': 'array', 'items': {'type': 'string'}},
                            }
                        }
                    }
                }
            ),
        }
    )
    def patch(self, request, format=None):
        channel_data = request.data.dict()

        updated_channel = serializers.UpdateChannelSerializer(
            request.user.current_channel,
            data=channel_data,
            partial=True
        )

        if not updated_channel.is_valid():
            return Response({
                'errors': updated_channel.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('banner') is not None:
            try:
                banner_image_url = CloudinaryUploader.upload_image(channel_data.get('banner'), 'banners')
                updated_channel.validated_data['banner_url'] = banner_image_url
            except:
                return Response({
                    'message': 'Failed to upload channel banner, please try again later'
                }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('picture') is not None:
            try:
                picture_image_url = CloudinaryUploader.upload_image(channel_data.get('picture'), 'pictures')
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

    @extend_schema(
        summary='Delete channel',
        description='User can delete a channel',
        responses={
            200: OpenApiResponse(
                description='Channel deleted successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='Channel does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='The channel is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='Cannot delete current channel',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
        }
    )
    def delete(self, request, channel_id, format=None):
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
