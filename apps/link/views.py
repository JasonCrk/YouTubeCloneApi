from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.link.serializers import CreateLinkSerializer


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

