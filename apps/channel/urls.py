from django.urls import path

from apps.channel import views

urlpatterns = [
    path('create/', views.CreateChannelView.as_view(), name='create_channel'),
    path('switch/', views.SwitchChannelView.as_view(), name='switch_channel'),
    path('subscribe/', views.SubscribeAndUnsubscribeChannelView.as_view(), name='subscribe_unsubscribe_channel'),
    path('edit/', views.EditChannelView.as_view(), name='edit_channel'),
    path('<int:channel_id>/delete/', views.DeleteChannelView.as_view(), name='delete_channel')
]