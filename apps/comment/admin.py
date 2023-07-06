from django.contrib import admin

from apps.comment.models import Comment

class CommentAdmin(admin.ModelAdmin):
    list_display = ['profile', 'video', 'comment', 'publication_date', 'was_edited']
    list_filter = ['was_edited']
    search_fields = ['content']
    ordering = ['content']

admin.site.register(Comment, CommentAdmin)