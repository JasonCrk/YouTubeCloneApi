from django.contrib import admin

from apps.video.models import Video

class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'channel', 'video_url', 'publication_date']
    search_fields = ['title', 'description']
    ordering = ['title']

admin.site.register(Video, VideoAdmin)
