from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Like, Follow, Notification
from posts.models import Post, Comment


@receiver(post_save, sender=Like)
def update_like_count_on_create(sender, instance, created, **kwargs):
    """Update like count when a like is created."""
    if created:
        if instance.post:
            instance.post.likes_count += 1
            instance.post.save(update_fields=['likes_count'])
            
            # Create notification for post like
            if instance.user != instance.post.author:
                Notification.objects.create(
                    recipient=instance.post.author,
                    sender=instance.user,
                    notification_type='like',
                    post=instance.post
                )


@receiver(post_delete, sender=Like)
def update_like_count_on_delete(sender, instance, **kwargs):
    """Update like count when a like is deleted."""
    if instance.post:
        instance.post.likes_count = max(0, instance.post.likes_count - 1)
        instance.post.save(update_fields=['likes_count'])


@receiver(post_save, sender=Follow)
def update_follow_count_on_create(sender, instance, created, **kwargs):
    """Update follow counts when a follow relationship is created."""
    if created:
        # Update follower's following count
        follower_profile = instance.follower.profile
        follower_profile.following_count += 1
        follower_profile.save(update_fields=['following_count'])
        
        # Update following's followers count
        following_profile = instance.following.profile
        following_profile.followers_count += 1
        following_profile.save(update_fields=['followers_count'])
        
        # Create notification for follow
        Notification.objects.create(
            recipient=instance.following,
            sender=instance.follower,
            notification_type='follow'
        )


@receiver(post_delete, sender=Follow)
def update_follow_count_on_delete(sender, instance, **kwargs):
    """Update follow counts when a follow relationship is deleted."""
    # Update follower's following count
    follower_profile = instance.follower.profile
    follower_profile.following_count = max(0, follower_profile.following_count - 1)
    follower_profile.save(update_fields=['following_count'])
    
    # Update following's followers count
    following_profile = instance.following.profile
    following_profile.followers_count = max(0, following_profile.followers_count - 1)
    following_profile.save(update_fields=['followers_count'])


@receiver(post_save, sender=Post)
def update_post_count_on_create(sender, instance, created, **kwargs):
    """Update post count when a post is created."""
    if created:
        profile = instance.author.profile
        profile.posts_count += 1
        profile.save(update_fields=['posts_count'])


@receiver(post_delete, sender=Post)
def update_post_count_on_delete(sender, instance, **kwargs):
    """Update post count when a post is deleted."""
    profile = instance.author.profile
    profile.posts_count = max(0, profile.posts_count - 1)
    profile.save(update_fields=['posts_count'])


@receiver(post_save, sender=Comment)
def update_comment_count_on_create(sender, instance, created, **kwargs):
    """Update comment count when a comment is created."""
    if created:
        instance.post.comments_count += 1
        instance.post.save(update_fields=['comments_count'])
        
        # Create notification for comment
        if instance.author != instance.post.author:
            Notification.objects.create(
                recipient=instance.post.author,
                sender=instance.author,
                notification_type='comment',
                post=instance.post,
                comment=instance
            )


@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    """Update comment count when a comment is deleted."""
    instance.post.comments_count = max(0, instance.post.comments_count - 1)
    instance.post.save(update_fields=['comments_count'])
