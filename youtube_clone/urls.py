from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/channels/', include('apps.channel.urls')),
    path('api/videos/', include('apps.video.urls')),

    path('admin/', admin.site.urls)
]
