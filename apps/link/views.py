from django.db.models import F

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.link.models import Link
from apps.channel.models import Channel

from apps.link.serializers import LinkListSerializer, CreateLinkSerializer, UpdateLinkSerializer


class GetChannelLinksView(APIView):
    def get(self, request, channel_id, format=None):
        try:
            channel = Channel.objects.get(id=channel_id)
        except Channel.DoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel_links = Link.objects.filter(channel=channel).order_by('position')

        serialized_channel_links = LinkListSerializer(channel_links, many=True)

        return Response({
            'data': serialized_channel_links.data
        }, status=status.HTTP_200_OK)


class CreateLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        new_link = CreateLinkSerializer(data={
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

    def post(self, request, format=None):
        try:
            link_id = int(request.data.get('link_id'))
        except (ValueError, TypeError):
            return Response({
                'message': 'The link ID must be a number'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_position = int(request.data.get('new_position'))
        except (ValueError, TypeError):
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
        ).exclude(id=link.pk).order_by('position')

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

    def put(self, request, link_id, format=None):
        try:
            link: Link = Link.objects.get(id=link_id)
        except Link.DoesNotExist:
            return Response({
                'message': 'The link does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        link_updated = UpdateLinkSerializer(link, data=request.data)

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
