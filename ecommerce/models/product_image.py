from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from io import BytesIO
import logging
import uuid

logger = logging.getLogger(__name__)

# Longest side in px. thumbnail: catalog cards/cart; medium: product detail and zoom.
THUMBNAIL_SIZE = 600
MEDIUM_SIZE = 1600


def get_word(): return 'dev' if settings.ENV == 'DEVELOPMENT' else 'prod'


def variant_name(image_name, suffix):
    return f"{image_name.rsplit('.', 1)[0]}_{suffix}.webp"


class ProductImage(models.Model):
    def get_path(instance, filename):
        extension = filename.split('.')[-1]
        generated = uuid.uuid1().hex
        return f'ecommerce/{get_word()}/product_images/{generated}.{extension}'

    def get_path_thumbnail(instance, filename):
        extension = filename.split('.')[-1]
        filename = filename.replace(f'.{extension}', '')
        return f'ecommerce/{get_word()}/product_images/{filename}_thumbnail.{extension}'


    image = models.ImageField(upload_to=get_path)
    thumbnail = models.ImageField(upload_to=get_path_thumbnail, blank=True, null=True)
    order_index = models.IntegerField(default=0)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    is_main = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Imagen de producto'
        verbose_name_plural = 'Imagenes de productos'
        ordering = ['order_index', '-id', '-updated_at']

    def has_variants(self):
        return bool(self.image) and self.thumbnail.name == variant_name(self.image.name, 'thumb')

    def medium_url(self):
        # ponytail: medium lives next to the thumbnail by naming convention (no extra column/migration).
        if self.has_variants():
            return self.image.storage.url(variant_name(self.image.name, 'medium'))
        return self.image.url if self.image else None

    def generate_variants(self):
        """Writes WebP thumbnail + medium next to the original (never touched). Idempotent."""
        self.image.open('rb')
        try:
            img = Image.open(self.image)
            img.draft('RGB', (MEDIUM_SIZE, MEDIUM_SIZE))  # JPEG: decode at reduced scale, saves RAM/CPU
            img = ImageOps.exif_transpose(img)
            img = img.convert('RGBA' if img.mode in ('RGBA', 'LA', 'P') else 'RGB')
            for suffix, size in (('medium', MEDIUM_SIZE), ('thumb', THUMBNAIL_SIZE)):
                img.thumbnail((size, size), Image.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format='WEBP', quality=80, method=4)
                name = self.image.storage.save(variant_name(self.image.name, suffix), ContentFile(buffer.getvalue()))
        finally:
            self.image.close()
        self.thumbnail.name = name
        super().save(update_fields=['thumbnail'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.has_variants():
            try:
                self.generate_variants()
            except Exception:
                # Never lose an upload because of a bad image: the original keeps being served.
                logger.exception('Could not generate variants for ProductImage %s', self.pk)
