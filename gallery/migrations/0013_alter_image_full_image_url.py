# Generated by Django 4.0.5 on 2024-08-07 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0012_remove_image_gallery_image_url_image_gallery_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='full_image_url',
            field=models.URLField(default='https://via.placeholder.com/512', max_length=300),
        ),
    ]