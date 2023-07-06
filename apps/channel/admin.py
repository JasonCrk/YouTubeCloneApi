from django.contrib import admin

from apps.channel.models import Channel, ChannelSubscription

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'handle', 'joined']
    search_fields = ['handle']
    ordering = ['user_profile']

class ChannelSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'channel', 'subscription_date']
    ordering = ['profile']

admin.site.register(Channel, ChannelAdmin)
admin.site.register(ChannelSubscription, ChannelSubscriptionAdmin)