from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
import uuid
import base64

def get_word(): return 'dev' if settings.ENV == 'DEVELOPMENT' else 'prod'

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