from django.urls import path

from apps.link import views

urlpatterns = [
    path('channel/<int:channel_id>', views.RetrieveChannelLinksView.as_view(), name='get_channel_links'),
    path('create/', views.CreateLinkView.as_view(), name='create_link'),
    path('reposition/', views.RepositionLinkView.as_view(), name='reposition_link'),
    path('<int:link_id>/edit/', views.EditLinkView.as_view(), name='edit_link'),
    path('<int:link_id>/delete/', views.DeleteLinkView.as_view(), name='delete_link')
]