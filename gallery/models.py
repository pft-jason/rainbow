from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PilImage
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import boto3
import logging
import uuid

logger = logging.getLogger(__name__)

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Tag(models.Model):
    CategoryChoices = (
        ('age', 'Age'),
        ('body', 'Body'),
        ('ethnicity', 'Ethnicity'),
        ('interest', 'Interest')
    )
    category = models.CharField(max_length=100, choices=CategoryChoices)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class OfficialTag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Image(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery_images/', default='gallery_images/default.jpg')
    full_image_url = models.URLField(max_length=500, default='https://via.placeholder.com/512')
    gallery_image = models.ImageField(upload_to='gallery_images/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    official_tag = models.ManyToManyField(OfficialTag, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_images', blank=True)
    downloads = models.IntegerField(default=0)
    moderated = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.image and not self.gallery_image:
            img = PilImage.open(self.image)
            output_size = (512, 512)  # Define the size for the gallery image
            img.thumbnail(output_size)
            
            # Save the resized image to the gallery_image field
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            random_name = f'{uuid.uuid4()}.jpeg'
            self.gallery_image.save("gallery." + random_name, ContentFile(buffer.read()), save=False)
            
            # Set the full image URL
            if settings.ENVIRONMENT == 'production':
                self.full_image_url = default_storage.url("full." + random_name)
            else:
                self.full_image_url = default_storage.url("full." + random_name)
            
            super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.image:
            try:
                if settings.ENVIRONMENT == 'development':
                    default_storage.delete(self.image.name)
                else:
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
            except PermissionError as e:
                logger.error(f"PermissionError: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}") 

        if self.gallery_image:
            try:
                if settings.ENVIRONMENT == 'development':
                    default_storage.delete(self.gallery_image.name)
                else:
                    s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.gallery_image.name)
            except PermissionError as e:
                logger.error(f"PermissionError: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

        super().delete(*args, **kwargs)

class Comment(models.Model):
    image = models.ForeignKey(Image, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.image.title}'

