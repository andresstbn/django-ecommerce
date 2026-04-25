from django.db import models

def get_default_settings():
    return {
        'color': '',
        'icon': '',
        'discount_percentage': 0,
    }

class Brand(models.Model):
    commerce = models.ForeignKey('Commerce', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Nombre')
    settings = models.JSONField(default=dict, blank=True, verbose_name='Configuración')
    
    def get_is_erasable(self):
        return not self.products.exists()
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
    
    def __str__(self):
        return self.name

class Category(models.Model):
    commerce = models.ForeignKey('Commerce', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(default='', verbose_name='Descripción', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Categoría padre')
    settings = models.JSONField(default=get_default_settings, blank=True, verbose_name='Configuración')
    
    def get_is_erasable(self):
        return not self.products.exists()
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorias'
        unique_together = ['commerce', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name