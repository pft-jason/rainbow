from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PilImage
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from dirtydeedz.s3_client import client as s3_client

import logging
import uuid

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
    full_image = models.ImageField(upload_to='', default='default.jpg')
    full_image_url = models.URLField(max_length=500, default='https://via.placeholder.com/512')
    gallery_image = models.ImageField(upload_to='', default='default.jpg')
    gallery_image_url = models.URLField(max_length=500, default='https://via.placeholder.com/512')
    title = models.CharField(max_length=100) 
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    official_tag = models.ManyToManyField(OfficialTag, blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_images', blank=True)
    downloads = models.IntegerField(default=0) 
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    moderated = models.BooleanField(default=False)

    def __str__(self):
        return self.title            
    
    def delete(self, *args, **kwargs):
        if self.full_image:
           response = s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.full_image.name)

        if self.gallery_image:
            response = s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.gallery_image.name)
       
        super().delete(*args, **kwargs)

class Comment(models.Model):
    image = models.ForeignKey(Image, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.image.title}'

