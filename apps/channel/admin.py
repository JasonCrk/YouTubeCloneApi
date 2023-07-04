from django.contrib import admin

from apps.channel.models import Channel

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'handle', 'joined']
    search_fields = ['handle']
    ordering = ['user_profile']

admin.site.register(Channel, ChannelAdmin)