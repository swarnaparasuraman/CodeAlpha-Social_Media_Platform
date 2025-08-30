from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_preview', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['author__username', 'content']
    readonly_fields = ['likes_count', 'comments_count', 'created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'post', 'content_preview', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['author__username', 'content', 'post__content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:30] + '...' if len(obj.content) > 30 else obj.content
    content_preview.short_description = 'Content Preview'
