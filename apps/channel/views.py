from django.core.exceptions import ObjectDoesNotExist
from django.db import Error as DBError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from apps.channel.models import Channel, ChannelSubscription

from apps.channel.serializers import ChannelSerializer

from cloudinary.exceptions import Error as CloudinaryUpdateError
from youtube_clone.utils.storage import upload_image


class CreateChannel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        channel_data = request.data

        channel_validation = ChannelSerializer(data={'name': channel_data['name']})

        if not channel_validation.is_valid():
            return Response({
                'errors': channel_validation.errors
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        if Channel.objects.filter(user=request.user).count() == 10:
            return Response({
                'message': "You can't have more than 10 channels"
            }, status=status.HTTP_400_BAD_REQUEST)

        Channel.create(
            handle=channel_data['name'],
            name=channel_data['name'],
            user=request.user
        ).save()

        return Response({
            'message': 'The channel has been created'
        }, status=status.HTTP_200_OK)


class SubscribeAndUnsubscribeChannel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            channel_id = int(request.data['channel_id'])
        except:
            return Response({
                'message': 'The channel ID must be a number'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            channel = Channel.objects.get(id=channel_id)
        except ObjectDoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel.user.pk == request.user.pk:
            return Response({
                'message': "You can't subscribe to a channel that's yours"
            }, status=status.HTTP_400_BAD_REQUEST)

        if ChannelSubscription.objects.filter(user=request.user, channel=channel):
            channel_subscription = ChannelSubscription.objects.get(user=request.user, channel=channel)
            channel_subscription.delete()

            return Response({
                'message': 'Subscription removed'
            }, status=status.HTTP_200_OK)

        channel.subscription.add(request.user)

        return Response({
            'message': 'Subscription added'
        }, status=status.HTTP_200_OK)


class EditChannel(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [FormParser, MultiPartParser]

    def patch(self, request, channel_id, format=None):
        channel_data = request.data.dict()

        if len(channel_data.keys()) == 0:
            return Response({
                'message': 'You need to update at least one attribute'
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            channel = Channel.objects.get(id=channel_id)
        except ObjectDoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel.user.pk != request.user.pk:
            return Response({
                'message': 'You are not a owner of this channel'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if channel_data.get('banner') != None:
            try:
                banner_image_url = upload_image(channel_data.get('banner'), 'banners')
                channel.banner = banner_image_url
            except CloudinaryUpdateError:
                return Response({
                    'message': 'Failed to update banner'
                }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('picture') != None:
            try:
                picture_image_url = upload_image(channel_data.get('picture'), 'pictures')
                channel.picture = picture_image_url
            except CloudinaryUpdateError:
                return Response({
                    'message': 'Failed to update picture'
                }, status=status.HTTP_400_BAD_REQUEST)

        if channel_data.get('description') != None:
            channel.description = channel_data.get('description')

        if channel_data.get('handle') != None:
            channel.handle = channel_data.get('handle')

        if channel_data.get('contact_email') != None:
            channel.contact_email = channel_data.get('contact_email')

        channel.save()

        return Response({
            'message': 'The channel has been successfully updated'
        }, status=status.HTTP_200_OK)


class DeleteChannel(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id, format=None):
        if Channel.objects.filter(user__pk=request.user.pk).count() < 2:
            return Response({
                'message': "You can't delete your last channel"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = Channel.objects.get(id=channel_id)
        except ObjectDoesNotExist:
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        if channel.user.pk != request.user.pk:
            return Response({
                'message': 'You are not a owner of this channel'
            }, status=status.HTTP_401_UNAUTHORIZED)

        try:
            channel.delete()
        except DBError:
            return Response({
                'message': 'The channel could not be deleted, please try again later'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'message': 'The channel has been deleted'
        }, status=status.HTTP_200_OK)
