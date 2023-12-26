from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/channels/', include('apps.channel.urls')),
    path('api/videos/', include('apps.video.urls')),
    path('api/comments/', include('apps.comment.urls')),
    path('api/links/', include('apps.link.urls')),
    path('api/playlists/', include('apps.playlist.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/docs', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger_ui'),

    path('admin/', admin.site.urls)
]
