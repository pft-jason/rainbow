from django.core.management.base import BaseCommand
from gallery.models import Image
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Delete images that are not used by any image in the database'

    def handle(self, *args, **kwargs):
        # Get all image file paths from the media directory
        media_root = settings.MEDIA_ROOT
        all_image_files = set()
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    all_image_files.add(os.path.normpath(os.path.join(root, file)))

        # Debug output
        self.stdout.write(self.style.SUCCESS(f'All image files: {all_image_files}'))

        # Get all image paths used in the database
        used_image_files = set()
        for image in Image.objects.all():
            used_image_files.add(os.path.normpath(os.path.join(media_root, image.image.name)))
            if image.gallery_image:
                used_image_files.add(os.path.normpath(os.path.join(media_root, image.gallery_image.name)))

        # Debug output
        self.stdout.write(self.style.SUCCESS(f'Used image files: {used_image_files}'))

        # Find unused images
        unused_image_files = all_image_files - used_image_files

        # Debug output
        self.stdout.write(self.style.SUCCESS(f'Unused image files: {unused_image_files}'))

        # Delete unused images
        for file_path in unused_image_files:
            try:
                os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f'Deleted unused image: {file_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting {file_path}: {e}'))