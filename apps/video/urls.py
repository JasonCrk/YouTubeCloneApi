from django.urls import path

from .views import CreateVideo

urlpatterns = [
    path('create/', CreateVideo.as_view(), name='upload_video')
]