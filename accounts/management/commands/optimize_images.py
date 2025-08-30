from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image
import os
from accounts.models import UserProfile
from posts.models import Post


class Command(BaseCommand):
    help = 'Optimize all images in the media directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='JPEG quality (1-100, default: 85)',
        )
        parser.add_argument(
            '--max-size',
            type=int,
            default=1200,
            help='Maximum image dimension (default: 1200px)',
        )

    def handle(self, *args, **options):
        quality = options['quality']
        max_size = options['max_size']
        
        self.stdout.write('Starting image optimization...')
        
        # Optimize profile pictures
        profiles = UserProfile.objects.exclude(profile_picture='profile_pics/default.jpg')
        for profile in profiles:
            if profile.profile_picture and os.path.exists(profile.profile_picture.path):
                self.optimize_image(profile.profile_picture.path, quality, 300)  # Profile pics smaller
                
        # Optimize post images
        posts = Post.objects.exclude(image='')
        for post in posts:
            if post.image and os.path.exists(post.image.path):
                self.optimize_image(post.image.path, quality, max_size)
                
        self.stdout.write(
            self.style.SUCCESS('Successfully optimized all images!')
        )

    def optimize_image(self, image_path, quality, max_size):
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(image_path, 'JPEG', quality=quality, optimize=True)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error optimizing {image_path}: {str(e)}')
            )
