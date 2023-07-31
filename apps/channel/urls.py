from django.urls import path

from apps.channel import views

urlpatterns = [
    path('subscribed', views.GetSubscribedChannelsView.as_view(), name='subscribed_channels'),
    path('search/', views.SearchChannelsView.as_view(), name='search_channels'),
    path('create/', views.CreateChannelView.as_view(), name='create_channel'),
    path('switch/', views.SwitchChannelView.as_view(), name='switch_channel'),
    path('subscribe/', views.SubscribeChannelView.as_view(), name='subscribe_channel'),
    path('edit/', views.EditChannelView.as_view(), name='edit_channel'),
    path('by-id/<pk>', views.GetChannelDetailsByIdView.as_view(), name='channel_details_by_id'),
    path('by-handle/<str:channel_handle>', views.GetChannelDetailsByHandleView.as_view(), name='channel_details_by_handle'),
    path('<int:channel_id>/delete/', views.DeleteChannelView.as_view(), name='delete_channel')
]