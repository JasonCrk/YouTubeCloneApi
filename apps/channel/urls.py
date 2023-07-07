from django.urls import path

from .views import SubscribeAndUnsubscribeChannel

urlpatterns = [
    path('subscribe/', SubscribeAndUnsubscribeChannel.as_view(), name='subscribe_unsubscribe_channel')
]