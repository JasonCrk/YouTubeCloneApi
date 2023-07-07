from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.contrib.auth import get_user_model

from apps.channel.models import Channel, ChannelSubscription

User = get_user_model()

class SubscribeAndUnsubscribeChannel(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            channel_id = int(request.data['channel_id'])
        except:
            return Response({
                'message': 'The channel ID must be a number'
            }, status=status.HTTP_406_NOT_ACCEPTABLE)

        if not Channel.objects.filter(id=channel_id).exists():
            return Response({
                'message': 'The channel does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

        channel = Channel.objects.get(id=channel_id)

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
