from django.urls import path

from .views import SubscribeAndUnsubscribeChannel, EditChannel

urlpatterns = [
    path('subscribe/', SubscribeAndUnsubscribeChannel.as_view(), name='subscribe_unsubscribe_channel'),
    path('<int:channel_id>/', EditChannel.as_view(), name='edit_channel')
]