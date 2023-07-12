from django.urls import path

from .views import SubscribeAndUnsubscribeChannel, EditChannel, DeleteChannel, CreateChannel

urlpatterns = [
    path('create/', CreateChannel.as_view(), name='create_channel'),
    path('subscribe/', SubscribeAndUnsubscribeChannel.as_view(), name='subscribe_unsubscribe_channel'),
    path('<int:channel_id>/', EditChannel.as_view(), name='edit_channel'),
    path('<int:channel_id>/delete', DeleteChannel.as_view(), name='delete_channel')
]