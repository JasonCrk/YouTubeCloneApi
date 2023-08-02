from django.urls import path

from apps.link import views

urlpatterns = [
    path('create/', views.CreateLinkView.as_view(), name='create_link')
]