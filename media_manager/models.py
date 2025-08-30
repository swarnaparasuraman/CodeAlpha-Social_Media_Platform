from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from PIL import Image
import os
import uuid


class MediaFile(models.Model):
    """Advanced media file model with optimization and metadata"""

    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_files')

    # File information
    original_file = models.FileField(upload_to='media/original/%Y/%m/')
    optimized_file = models.FileField(upload_to='media/optimized/%Y/%m/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='media/thumbnails/%Y/%m/', blank=True, null=True)

    # Metadata
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # in bytes
    mime_type = models.CharField(max_length=100)

    # Image/Video specific
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # for videos/audio

    # Processing status
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)

    # SEO and accessibility
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'media_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.media_type})"

    @property
    def file_size_human(self):
        """Return human readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"

    @property
    def aspect_ratio(self):
        """Calculate aspect ratio for images/videos"""
        if self.width and self.height:
            return self.width / self.height
        return None

    def save(self, *args, **kwargs):
        if not self.pk:  # New file
            self.process_file()
        super().save(*args, **kwargs)

    def process_file(self):
        """Process the uploaded file based on type"""
        if self.media_type == 'image':
            self.process_image()
        elif self.media_type == 'video':
            self.process_video()

    def process_image(self):
        """Optimize and create thumbnails for images"""
        try:
            with Image.open(self.original_file.path) as img:
                # Get dimensions
                self.width, self.height = img.size

                # Create optimized version
                optimized = img.copy()
                if optimized.mode in ('RGBA', 'P'):
                    optimized = optimized.convert('RGB')

                # Resize if too large
                max_size = (1920, 1920)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    optimized.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Save optimized version
                optimized_path = self.original_file.path.replace('original', 'optimized')
                os.makedirs(os.path.dirname(optimized_path), exist_ok=True)
                optimized.save(optimized_path, 'JPEG', quality=85, optimize=True)

                # Create thumbnail
                thumbnail = img.copy()
                thumbnail.thumbnail((300, 300), Image.Resampling.LANCZOS)
                thumbnail_path = self.original_file.path.replace('original', 'thumbnails')
                os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
                thumbnail.save(thumbnail_path, 'JPEG', quality=80)

                self.is_processed = True

        except Exception as e:
            self.processing_error = str(e)

    def process_video(self):
        """Process video files (placeholder for video processing)"""
        # This would integrate with FFmpeg or similar for video processing
        # For now, just mark as processed
        self.is_processed = True


class MediaCollection(models.Model):
    """Collections/Albums for organizing media"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cover_image = models.ForeignKey(MediaFile, on_delete=models.SET_NULL, null=True, blank=True)
    media_files = models.ManyToManyField(MediaFile, related_name='collections')

    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} by {self.user.username}"

    @property
    def media_count(self):
        return self.media_files.count()


class MediaTag(models.Model):
    """Tags for media files"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class MediaFileTag(models.Model):
    """Many-to-many relationship between media files and tags"""

    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE)
    tag = models.ForeignKey(MediaTag, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['media_file', 'tag']

    def __str__(self):
        return f"{self.media_file.file_name} - {self.tag.name}"
