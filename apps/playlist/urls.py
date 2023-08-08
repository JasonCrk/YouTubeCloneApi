from django.urls import path

from apps.playlist import views

urlpatterns = [
    path('create/', views.CreatePlaylistView.as_view(), name='create_playlist')
]