from django.core.cache import cache
from django.db.models import Prefetch
from posts.models import Post, Comment
from social.models import Like, Follow
from accounts.models import UserProfile


def get_optimized_posts_queryset():
    """
    Get an optimized queryset for posts with all related data prefetched.
    """
    return Post.objects.select_related(
        'author__profile'
    ).prefetch_related(
        'likes',
        Prefetch(
            'comments',
            queryset=Comment.objects.select_related('author__profile')
        )
    )


def get_user_feed_posts(user, page_size=10):
    """
    Get optimized feed posts for a user with caching.
    """
    cache_key = f'user_feed_{user.id}_{page_size}'
    cached_posts = cache.get(cache_key)
    
    if cached_posts is not None:
        return cached_posts
    
    # Get following users
    following_users = Follow.objects.filter(
        follower=user
    ).values_list('following', flat=True)
    
    # Get posts from following users + own posts
    posts = get_optimized_posts_queryset().filter(
        author__in=list(following_users) + [user.id]
    )[:page_size]
    
    # Cache for 5 minutes
    cache.set(cache_key, posts, 300)
    return posts


def get_user_notifications_count(user):
    """
    Get unread notifications count with caching.
    """
    cache_key = f'notifications_count_{user.id}'
    count = cache.get(cache_key)
    
    if count is not None:
        return count
    
    from social.models import Notification
    count = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).count()
    
    # Cache for 1 minute
    cache.set(cache_key, count, 60)
    return count


def invalidate_user_cache(user):
    """
    Invalidate all cache entries for a user.
    """
    cache_keys = [
        f'user_feed_{user.id}_10',
        f'user_feed_{user.id}_20',
        f'notifications_count_{user.id}',
        f'user_profile_{user.id}',
    ]
    cache.delete_many(cache_keys)


def get_trending_posts(limit=20):
    """
    Get trending posts based on recent likes and comments.
    """
    cache_key = f'trending_posts_{limit}'
    cached_posts = cache.get(cache_key)
    
    if cached_posts is not None:
        return cached_posts
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Get posts from last 7 days with high engagement
    week_ago = timezone.now() - timedelta(days=7)
    posts = get_optimized_posts_queryset().filter(
        created_at__gte=week_ago
    ).order_by('-likes_count', '-comments_count', '-created_at')[:limit]
    
    # Cache for 30 minutes
    cache.set(cache_key, posts, 1800)
    return posts


def get_suggested_users(user, limit=5):
    """
    Get suggested users to follow based on mutual connections.
    """
    cache_key = f'suggested_users_{user.id}_{limit}'
    cached_users = cache.get(cache_key)
    
    if cached_users is not None:
        return cached_users
    
    # Get users that current user's following are following
    following_users = Follow.objects.filter(
        follower=user
    ).values_list('following', flat=True)
    
    # Get users followed by people the current user follows
    suggested_user_ids = Follow.objects.filter(
        follower__in=following_users
    ).exclude(
        following=user
    ).exclude(
        following__in=following_users
    ).values_list('following', flat=True).distinct()[:limit * 2]
    
    # Get user profiles
    suggested_users = UserProfile.objects.filter(
        user__in=suggested_user_ids
    ).select_related('user')[:limit]
    
    # Cache for 1 hour
    cache.set(cache_key, suggested_users, 3600)
    return suggested_users


class CacheKeys:
    """
    Centralized cache key management.
    """
    USER_FEED = 'user_feed_{user_id}_{page_size}'
    USER_NOTIFICATIONS = 'notifications_count_{user_id}'
    USER_PROFILE = 'user_profile_{user_id}'
    TRENDING_POSTS = 'trending_posts_{limit}'
    SUGGESTED_USERS = 'suggested_users_{user_id}_{limit}'
    POST_LIKES = 'post_likes_{post_id}'
    POST_COMMENTS = 'post_comments_{post_id}'
