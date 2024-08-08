import uuid
from django.core.management.base import BaseCommand
from gallery.models import Image
from PIL import Image as PilImage
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Generate gallery images for all existing images without a gallery image or where the gallery image file is missing'

    def handle(self, *args, **kwargs):
        images = Image.objects.filter(gallery_image__isnull=True) | Image.objects.filter(gallery_image__isnull=False)
        for image in images:
            gallery_image_path = os.path.join(settings.MEDIA_ROOT, image.gallery_image.name) if image.gallery_image else None
            
            # Check if the gallery image file exists
            if not gallery_image_path or not os.path.isfile(gallery_image_path):
                img = PilImage.open(image.image.path)
                output_size = (300, 300)  # Define the size for the gallery image
                img.thumbnail(output_size)
                
                # Save the resized image to the gallery_image field
                random_name = f'{uuid.uuid4()}.jpeg'
                gallery_image_path = os.path.join('gallery_images', random_name)
                img.save(os.path.join(settings.MEDIA_ROOT, gallery_image_path))
                image.gallery_image = gallery_image_path
                image.save()
                self.stdout.write(self.style.SUCCESS(f'Generated gallery image for {image.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Gallery image already exists for {image.title}'))