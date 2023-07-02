from django.contrib import admin

from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'picture', 'theme', 'languages']
    list_filter = ['theme', 'languages']
    fieldsets = [
        (None, { 'fields': ['user', 'picture'] }),
        ('Settings', { 'fields': ['theme', 'languages'] }),
    ]

    search_fields = ['theme', 'languages']
    ordering = ['user']
    filter_horizontal = []

admin.site.register(Profile, ProfileAdmin)