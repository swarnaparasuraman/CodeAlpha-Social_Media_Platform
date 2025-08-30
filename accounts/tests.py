from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_profile_creation(self):
        """Test that a user profile is automatically created when a user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_user_profile_str(self):
        """Test the string representation of UserProfile."""
        expected = f"{self.user.username}'s Profile"
        self.assertEqual(str(self.user.profile), expected)

    def test_full_name_property(self):
        """Test the full_name property."""
        # Test with no first/last name
        self.assertEqual(self.user.profile.full_name, 'testuser')

        # Test with first and last name
        self.user.first_name = 'John'
        self.user.last_name = 'Doe'
        self.user.save()
        self.assertEqual(self.user.profile.full_name, 'John Doe')


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')

    def test_register_view_get(self):
        """Test GET request to register view."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create your account')

    def test_register_view_post_valid(self):
        """Test POST request with valid data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_invalid(self):
        """Test POST request with invalid data."""
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'different',
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)  # Stay on form with errors
        self.assertFalse(User.objects.filter(username='newuser').exists())


class UserProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile_url = reverse('accounts:profile', kwargs={'username': 'testuser'})

    def test_profile_view_get(self):
        """Test GET request to profile view."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_view_nonexistent_user(self):
        """Test profile view for non-existent user."""
        url = reverse('accounts:profile', kwargs={'username': 'nonexistent'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class UserFormsTest(TestCase):
    def test_custom_user_creation_form_valid(self):
        """Test CustomUserCreationForm with valid data."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid(self):
        """Test CustomUserCreationForm with invalid data."""
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'different',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_profile_form_valid(self):
        """Test UserProfileForm with valid data."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        form_data = {
            'bio': 'This is my bio',
            'location': 'New York',
            'website': 'https://example.com',
        }
        form = UserProfileForm(data=form_data, instance=user.profile)
        self.assertTrue(form.is_valid())
