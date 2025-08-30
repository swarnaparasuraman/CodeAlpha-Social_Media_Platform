from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Like, Follow, Notification
from posts.models import Post, Comment


class LikeModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='This is a test post'
        )

    def test_like_creation(self):
        """Test like creation."""
        like = Like.objects.create(user=self.user2, post=self.post)
        self.assertEqual(like.user, self.user2)
        self.assertEqual(like.post, self.post)

    def test_like_str(self):
        """Test the string representation of Like."""
        like = Like.objects.create(user=self.user2, post=self.post)
        expected = f"{self.user2.username} likes post {self.post.id}"
        self.assertEqual(str(like), expected)

    def test_like_count_update(self):
        """Test that like count is updated when like is created."""
        initial_count = self.post.likes_count
        Like.objects.create(user=self.user2, post=self.post)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, initial_count + 1)

    def test_unique_like_constraint(self):
        """Test that a user can only like a post once."""
        Like.objects.create(user=self.user2, post=self.post)
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Like.objects.create(user=self.user2, post=self.post)


class FollowModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )

    def test_follow_creation(self):
        """Test follow creation."""
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        self.assertEqual(follow.follower, self.user1)
        self.assertEqual(follow.following, self.user2)

    def test_follow_str(self):
        """Test the string representation of Follow."""
        follow = Follow.objects.create(follower=self.user1, following=self.user2)
        expected = f"{self.user1.username} follows {self.user2.username}"
        self.assertEqual(str(follow), expected)

    def test_follow_count_update(self):
        """Test that follow counts are updated when follow is created."""
        initial_following_count = self.user1.profile.following_count
        initial_followers_count = self.user2.profile.followers_count

        Follow.objects.create(follower=self.user1, following=self.user2)

        self.user1.profile.refresh_from_db()
        self.user2.profile.refresh_from_db()

        self.assertEqual(self.user1.profile.following_count, initial_following_count + 1)
        self.assertEqual(self.user2.profile.followers_count, initial_followers_count + 1)

    def test_unique_follow_constraint(self):
        """Test that a user can only follow another user once."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Follow.objects.create(follower=self.user1, following=self.user2)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='This is a test post'
        )

    def test_notification_creation(self):
        """Test notification creation."""
        notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like',
            post=self.post
        )
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.notification_type, 'like')
        self.assertFalse(notification.is_read)

    def test_notification_str(self):
        """Test the string representation of Notification."""
        notification = Notification.objects.create(
            recipient=self.user1,
            sender=self.user2,
            notification_type='like',
            post=self.post
        )
        expected = f"{self.user2.username} like notification to {self.user1.username}"
        self.assertEqual(str(notification), expected)


class SocialViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user1,
            content='This is a test post'
        )

    def test_notifications_view(self):
        """Test notifications view."""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('social:notifications'))
        self.assertEqual(response.status_code, 200)

    def test_like_post_ajax(self):
        """Test liking a post via AJAX."""
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(
            reverse('posts:like', kwargs={'pk': self.post.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(user=self.user2, post=self.post).exists())
