from django.db.models import F

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse

from apps.link.models import Link
from apps.channel.models import Channel

from apps.link import serializers


class RetrieveChannelLinksView(APIView):
    @extend_schema(
        summary='Retrieve channel links',
        description='Get the links of a channel',
        responses={
            200: OpenApiResponse(
                description='Links of a channel',
                response=serializers.LinkListSerializer(many=True)
            ),
            404: OpenApiResponse(
                description='Channel does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def get(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel_links = Link.objects.filter(channel=channel)

        serialized_channel_links = serializers.LinkListSerializer(channel_links, many=True)

        return Response({
            'data': serialized_channel_links.data
        }, status=status.HTTP_200_OK)


class CreateLinkView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.CreateLinkSerializer

    @extend_schema(
        summary='Retrieve channel links',
        description='Get the links of a channel',
        request=inline_serializer(
            'CreateLink',
            fields={
                'title': serializers.serializers.CharField(),
                'url': serializers.serializers.URLField()
            }
        ),
        responses={
            201: OpenApiResponse(
                description='Link created successfully',
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
                                'title': {'type': 'array', 'items': {'type': 'string'}},
                                'url': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        }
                    }
                }
            )
        }
    )
    def post(self, request, format=None):
        new_link = serializers.CreateLinkSerializer(data={
            'title': request.data.get('title'),
            'url': request.data.get('url'),
            'channel': request.user.current_channel.pk
        })

        if not new_link.is_valid():
            return Response({
                'errors': new_link.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        new_link.save()

        return Response({
            'message': 'The link has been created'
        }, status=status.HTTP_201_CREATED)


class RepositionLinkView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Link

    @extend_schema(
        summary='Reposition link',
        description='Change the position of a link to the position of another link in the channel',
        request=inline_serializer(
            'RepositionLink',
            fields={
                'new_position': serializers.serializers.IntegerField()
            }
        ),
        responses={
            200: OpenApiResponse(
                description='Link successfully repositioned',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='The new position is not a number',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='The link does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='The link is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
        }
    )
    def post(self, request, link_id, format=None):
        try:
            new_position = int(request.data.get('new_position'))
        except:
            return Response({
                'message': 'The new position must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            link: Link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return Response({
                'message': 'The link does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if link.channel != request.user.current_channel:
            return Response({
                'message': 'You do not own this link'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if link.position == new_position:
            return Response({
                'message': 'The new position must not be the same as the link position'
            }, status=status.HTTP_400_BAD_REQUEST)

        current_channel = request.user.current_channel

        try:
            link_to_update: Link = Link.objects.get(
                channel=current_channel,
                position=new_position
            )
        except Link.DoesNotExist:
            return Response({
                'message': 'The new position does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel_links_rearrange = Link.objects.filter(
            channel=current_channel
        ).exclude(id=link.pk)

        if abs(link.position - new_position) == 1:
            link_to_update.position = link.position
            link_to_update.save()
        elif link.position > new_position:
            links_to_rearrange = channel_links_rearrange.filter(position__range=(new_position, link.position))
            links_to_rearrange.update(position=F('position') + 1)
        else:
            links_to_rearrange = channel_links_rearrange.filter(position__range=(link.position, new_position))
            links_to_rearrange.update(position=F('position') - 1)

        link.position = new_position
        link.save()

        return Response({
            'message': 'The link has been repositioned'
        }, status=status.HTTP_200_OK)


class EditLinkView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdateLinkSerializer

    @extend_schema(
        summary='Edit link',
        description='A channel can update a link',
        responses={
            200: OpenApiResponse(
                description='Link updated successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='The link does not exist',
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
                                'title': {'type': 'array', 'items': {'type': 'string'}},
                                'url': {'type': 'array', 'items': {'type': 'string'}}
                            }
                        }
                    }
                }
            ),
            401: OpenApiResponse(
                description='The link is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def put(self, request, link_id, format=None):
        try:
            link: Link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return Response({
                'message': 'The link does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        link_updated = serializers.UpdateLinkSerializer(link, data=request.data)

        if not link_updated.is_valid():
            return Response({
                'errors': link_updated.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        if link.channel != request.user.current_channel:
            return Response({
                'message': 'You do not own this link'
            }, status=status.HTTP_401_UNAUTHORIZED)

        link_updated.save()

        return Response({
            'message': 'The link has been updated'
        }, status=status.HTTP_200_OK)


class DeleteLinkView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Delete link',
        description='A channel can delete a link',
        responses={
            200: OpenApiResponse(
                description='Link deleted successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            404: OpenApiResponse(
                description='The link does not exist',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            ),
            401: OpenApiResponse(
                description='The link is not yours',
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            )
        }
    )
    def delete(self, request, link_id, format=None):
        try:
            link: Link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return Response({
                'message': 'The link does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if link.channel != request.user.current_channel:
            return Response({
                'message': 'You do not own this link'
            }, status=status.HTTP_401_UNAUTHORIZED)

        link.delete()

        return Response({
            'message': 'The link has been deleted'
        }, status=status.HTTP_200_OK)
