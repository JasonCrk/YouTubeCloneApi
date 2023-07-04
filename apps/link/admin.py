from django.contrib import admin

from apps.link.models import Link

class LinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'channel', 'position']
    list_filter = ['position']
    search_fields = ['title']
    ordering = ['title']

admin.site.register(Link, LinkAdmin)
