from django.db import models
import random
import string

class Coupon(models.Model):
    code = models.CharField(max_length=100, unique=True)
    discount = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE, blank=True, default=None)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_update_datetime = models.DateTimeField(auto_now=True)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return f"{self.code} - {self.discount}%"
    
    def generate_random_code(self, length=6):
        uppercases = string.ascii_uppercase
        generated_string = ''.join(random.choice(uppercases) for _ in range(length))
        return generated_string
        
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_random_code()
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'
        ordering = ['-creation_datetime']