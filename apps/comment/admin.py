from django.contrib import admin

from apps.comment.models import Comment, LikedComment

class CommentAdmin(admin.ModelAdmin):
    list_display = ['profile', 'video', 'comment', 'publication_date', 'was_edited']
    list_filter = ['was_edited']
    search_fields = ['content']
    ordering = ['content']

class LikedCommentAdmin(admin.ModelAdmin):
    list_display = ['profile', 'comment', 'liked']
    list_filter = ['liked']
    ordering = ['profile']

admin.site.register(Comment, CommentAdmin)
admin.site.register(LikedComment, LikedCommentAdmin)