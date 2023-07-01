from django.urls import path

from apps.user.views import ListUsers

urlpatterns = [
   path('', ListUsers.as_view())
]