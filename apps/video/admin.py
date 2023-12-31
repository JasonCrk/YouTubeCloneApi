from django.contrib import admin

from apps.video.models import Video, VideoView, LikedVideo

class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'channel', 'video_url', 'publication_date']
    search_fields = ['title', 'description']
    ordering = ['title']

class VideoViewAdmin(admin.ModelAdmin):
    list_display = ['channel', 'video', 'count', 'last_view_date']
    ordering = ['last_view_date']

class LikedVideoAdmin(admin.ModelAdmin):
    list_display = ['channel', 'video', 'liked']
    ordering = ['channel']

admin.site.register(Video, VideoAdmin)
admin.site.register(VideoView, VideoViewAdmin)
admin.site.register(LikedVideo, LikedVideoAdmin)
