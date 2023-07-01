from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.user.serializers import UserSerializer

User = get_user_model()

class ListUsers(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer_users = UserSerializer(users, many=True).data # type: ignore
        return Response({ 'data': serializer_users }, status.HTTP_200_OK)
