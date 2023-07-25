from django.core.exceptions import ObjectDoesNotExist
from django.db import Error as DBError
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from apps.channel.models import Channel, ChannelSubscription

from apps.channel.serializers import CreateChannelSerializer, UpdateChannelValidationSerializer

from youtube_clone.utils.storage import upload_image


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
        }, status=status.HTTP_200_OK)


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
        except ObjectDoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

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
        except ObjectDoesNotExist:
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
                'message': 'You need to update at least one attribute'
            }, status=status.HTTP_404_NOT_FOUND)

        updated_channel = UpdateChannelValidationSerializer(
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
        except ObjectDoesNotExist:
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

        try:
            channel.delete()
        except DBError:
            return Response({
                'message': 'The channel could not be deleted, please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'The channel has been deleted'
        }, status=status.HTTP_200_OK)
