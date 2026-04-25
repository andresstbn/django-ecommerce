from django.db import models

class OrderGroup(models.Model):
    name = models.CharField(max_length=100, default="", blank=True)
    prefix = models.CharField(max_length=100, default="", blank=True)
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE, blank=True, default=None)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_update_datetime = models.DateTimeField(auto_now=True)
    
    # Solicitud slack front
    
    code = models.CharField(max_length=50, default='', blank=True, verbose_name='Código')
    observations = models.TextField(default="", verbose_name="Observaciones", blank=True)
    web_default = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name} - {self.prefix}"
    
    class Meta:
        verbose_name = 'Grupo de pedidos'
        verbose_name_plural = 'Grupos de pedidos'
        ordering = ['-creation_datetime']

def get_default_extra_amounts(): # shipping
    return [{ 
        'type': 'shipping',
        'name': 'Envío',
        'amount': 0,
    }]
    
def get_default_delivery():
    return {
        'type': '',
        'shipping_company': 'Envío',
        'shipping_address': '',
        'tracking_number': '',
        'datetime': '',
        'observations': '',
    }
    
def get_default_taxes():
    return {
        "withholding": {
            "label": "Retención",
            "option": {
                "label": "",
                "percentage": 0,
                "value": 0,
            },
        }
    }
class Order(models.Model):
    group = models.ForeignKey("OrderGroup", on_delete=models.CASCADE, blank=True, null=True)
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE, blank=True, default=None)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_update_datetime = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, related_name="orders", blank=True, null=True)
    observations = models.TextField(default="", verbose_name="Observaciones", blank=True)
    payment_success = models.BooleanField(default=False)
    payment_datetime = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, default="", blank=True)
    payment_details = models.JSONField(default=dict, blank=True)
    subtotal_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    discount_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    code = models.CharField(max_length=50, default='', blank=True, verbose_name='Código')
    extra_amounts = models.JSONField(default=get_default_extra_amounts, blank=True)
    
    
    # DB-155
    state = models.CharField(max_length=100, default="", blank=True)
    delivery = models.JSONField(default=get_default_delivery, blank=True)
    taxes = models.JSONField(default=get_default_taxes, blank=True)
    payment_type = models.CharField(max_length=100, default="", blank=True)
    credit_days = models.IntegerField(default=0)
    
    
    def total_amount(self):
        total = 0
        for item in self.items.all():
            total += item.total_price()
            
        return float(total) #- float(self.discount_amount) ## TODO: Esto se desactivo para dejar los descuentos por item funcionales
    
    def __str__(self):
        prefix = self.group.prefix if self.group else ""
        customer_name = self.customer.name if self.customer else "-"
        return f"{prefix} {customer_name} - {self.creation_datetime}"
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-creation_datetime']
        
class OrderItem(models.Model):
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    variants = models.JSONField(default=dict, blank=True)
    variant_raw = models.CharField(max_length=100, default="")
    
    discounts = models.JSONField(default=dict, blank=True) # P.Ej { "coupon": 10, "global": 5}
    
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    
    
    def product_name(self):
        return self.product.name
    
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    class Meta: 
        verbose_name = 'Item de pedido'
        verbose_name_plural = 'Items de pedido'
        ordering = ['order', 'product']

 