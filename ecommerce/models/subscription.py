from django.db import models

class EmailSubscription(models.Model):
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_update_datetime = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=254)
    active = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verification_coupon = models.OneToOneField("Coupon", on_delete=models.CASCADE, blank=True, null=True, related_name="subscription")
    
    def __str__(self):
        return self.email
    
    def coupon_code(self):
        if not self.verification_coupon:
            return None
        return self.verification_coupon.code
    
    class Meta:
        verbose_name = 'Suscripción email'
        verbose_name_plural = 'Suscripciones email'
        ordering = ['-creation_datetime']