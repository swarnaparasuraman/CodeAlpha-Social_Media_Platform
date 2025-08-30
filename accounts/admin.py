from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'followers_count', 'following_count', 'posts_count', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'bio']
    readonly_fields = ['followers_count', 'following_count', 'posts_count', 'created_at', 'updated_at']

    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Full Name'
