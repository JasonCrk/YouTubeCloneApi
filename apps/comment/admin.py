from django.contrib import admin

from apps.comment.models import Comment, LikedComment

class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'comment', 'publication_date', 'was_edited']
    list_filter = ['was_edited']
    search_fields = ['content']
    ordering = ['content']

class LikedCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'liked']
    list_filter = ['liked']
    ordering = ['user']

admin.site.register(Comment, CommentAdmin)
admin.site.register(LikedComment, LikedCommentAdmin)