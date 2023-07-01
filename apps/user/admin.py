from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.user.models import UserAccount

class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_admin']
    list_filter = ['is_admin']
    fieldsets = [
        (None, { 'fields': ['email', 'username', 'password'] }),
        ('Personal Info', { 'fields': ['first_name', 'last_name'] }),
        ('Permissions', { 'fields': ['is_admin'] })
    ]

    search_fields = ['email']
    ordering = ['email']
    filter_horizontal = []

admin.site.register(UserAccount, UserAdmin)
admin.site.unregister(Group)
