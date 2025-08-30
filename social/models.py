from django.db import models
from django.contrib.auth.models import User
from posts.models import Post, Comment


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'likes'
        # Ensure a user can only like a post/comment once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_post_like',
                condition=models.Q(post__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_like',
                condition=models.Q(comment__isnull=False)
            ),
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['post']),
            models.Index(fields=['comment']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        if self.post:
            return f"{self.user.username} likes post {self.post.id}"
        elif self.comment:
            return f"{self.user.username} likes comment {self.comment.id}"
        return f"{self.user.username} like"

    def clean(self):
        # Ensure either post or comment is set, but not both
        if not self.post and not self.comment:
            raise ValueError("Like must be associated with either a post or comment")
        if self.post and self.comment:
            raise ValueError("Like cannot be associated with both post and comment")


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follows'
        # Ensure a user can only follow another user once
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follow'
            ),
            # Prevent self-following
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow'
            ),
        ]
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('mention', 'Mention'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username} {self.notification_type} notification to {self.recipient.username}"
