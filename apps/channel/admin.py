from django.contrib import admin

from apps.channel.models import Channel, ChannelSubscription

class ChannelAdmin(admin.ModelAdmin):
    list_display = ['user', 'handle', 'joined']
    search_fields = ['handle']
    ordering = ['user']

class ChannelSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'subscribing', 'subscription_date']
    ordering = ['subscriber']

admin.site.register(Channel, ChannelAdmin)
admin.site.register(ChannelSubscription, ChannelSubscriptionAdmin)