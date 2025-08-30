from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Post, Comment
from .forms import PostForm, CommentForm
from social.models import Like


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='This is a test post'
        )

    def test_post_creation(self):
        """Test post creation."""
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.content, 'This is a test post')
        self.assertEqual(self.post.likes_count, 0)
        self.assertEqual(self.post.comments_count, 0)

    def test_post_str(self):
        """Test the string representation of Post."""
        expected = f"{self.user.username} - This is a test post..."
        self.assertEqual(str(self.post), expected)

    def test_post_absolute_url(self):
        """Test get_absolute_url method."""
        expected_url = reverse('posts:detail', kwargs={'pk': self.post.pk})
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_time_since_posted(self):
        """Test time_since_posted property."""
        time_since = self.post.time_since_posted
        self.assertIn('now', time_since.lower())


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='This is a test post'
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment'
        )

    def test_comment_creation(self):
        """Test comment creation."""
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'This is a test comment')

    def test_comment_str(self):
        """Test the string representation of Comment."""
        expected = f"{self.user.username} on {self.post.id}: This is a test comment..."
        self.assertEqual(str(self.comment), expected)


class PostViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.post = Post.objects.create(
            author=self.user,
            content='This is a test post'
        )

    def test_feed_view_authenticated(self):
        """Test feed view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('posts:feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test post')

    def test_feed_view_unauthenticated(self):
        """Test feed view redirects unauthenticated users."""
        response = self.client.get(reverse('posts:feed'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_post_detail_view(self):
        """Test post detail view."""
        response = self.client.get(reverse('posts:detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This is a test post')

    def test_create_post_view_get(self):
        """Test GET request to create post view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('posts:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New Post')

    def test_create_post_view_post(self):
        """Test POST request to create post view."""
        self.client.login(username='testuser', password='testpass123')
        data = {'content': 'New test post'}
        response = self.client.post(reverse('posts:create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Post.objects.filter(content='New test post').exists())


class PostFormsTest(TestCase):
    def test_post_form_valid(self):
        """Test PostForm with valid data."""
        form_data = {'content': 'This is a test post'}
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_invalid(self):
        """Test PostForm with invalid data."""
        form_data = {'content': ''}  # Empty content
        form = PostForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_comment_form_valid(self):
        """Test CommentForm with valid data."""
        form_data = {'content': 'This is a test comment'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
