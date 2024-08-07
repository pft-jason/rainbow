from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PilImage
import os
from django.conf import settings


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
    image = models.ImageField(upload_to='images/')
    gallery_image = models.ImageField(upload_to='gallery_images/', blank=True, null=True)
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
            img = PilImage.open(self.image.path)
            output_size = (512, 512)  # Define the size for the gallery image
            img.thumbnail(output_size)
            
            # Save the resized image to the gallery_image field
            gallery_image_path = os.path.join('gallery_images', os.path.basename(self.image.name))
            img.save(os.path.join(settings.MEDIA_ROOT, gallery_image_path))
            self.gallery_image = gallery_image_path
            super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        if self.gallery_image:
            if os.path.isfile(self.gallery_image.path):
                os.remove(self.gallery_image.path)
        super().delete(*args, **kwargs)

class Comment(models.Model):
    image = models.ForeignKey(Image, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.image.title}'

