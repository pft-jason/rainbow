# Generated by Django 4.0.5 on 2024-08-08 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0013_alter_image_full_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='full_image_url',
            field=models.URLField(default='https://via.placeholder.com/512', max_length=500),
        ),
    ]
