from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model

from rest_framework.serializers import ModelSerializer

from apps.channel.serializers import CurrentChannelSerializer

User = get_user_model()

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'get_full_name'
        )

class UserAccountCreateSerializer(UserCreateSerializer):
    current_channel = CurrentChannelSerializer()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'current_channel'
        )
