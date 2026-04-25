from django.db import models
    
class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    commerce = models.ForeignKey('Commerce', on_delete=models.CASCADE, default=None, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Atributo'
        verbose_name_plural = 'Atributos'
        ordering = ['-id']
        

class AttributeValue(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    stock = models.IntegerField(default=0, verbose_name='Stock')
    attribute_options = models.ManyToManyField("AttributeOption", verbose_name='Opciones', blank=True, related_name='values')
    
    def __str__(self):
        return f"{(', ').join(self.get_attribute_option_names())}"
    
    def get_attribute_option_names(self):
        return self.attribute_options.values_list('name', flat=True)
    
    class Meta:
        verbose_name = 'Valor atributo'
        verbose_name_plural = 'Valores atributo'
        ordering = ['-id']
        
class AttributeOption(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    attribute = models.ForeignKey('ProductAttribute', on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=100, verbose_name='Etiqueta', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'
        ordering = ['-id']
        
    
    