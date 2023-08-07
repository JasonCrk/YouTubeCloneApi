from django.contrib import admin

from apps.playlist.models import Playlist, PlaylistVideo


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'visibility', 'created_at', 'updated_at']
    list_filter = ['visibility']
    search_fields = ['name']
    ordering = ['name']


class PlaylistVideoAdmin(admin.ModelAdmin):
    list_display = ['video', 'playlist', 'position', 'date_added']
    ordering = ['video']

admin.site.register(Playlist, PlaylistAdmin)
admin.site.register(PlaylistVideo, PlaylistVideoAdmin)
