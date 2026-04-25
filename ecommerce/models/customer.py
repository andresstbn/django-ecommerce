from django.db import models


class Customer(models.Model):
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE, blank=True, default=None)
    name = models.CharField(max_length=100, blank=True) #Legacy
    last_name = models.CharField(max_length=100, blank=True) #Legacy
    email = models.EmailField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    document_type = models.CharField(max_length=5, default='CC', blank=True)
    document_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, default="", blank=True)
    municipality = models.CharField(max_length=100, default="", blank=True)
    person_type = models.CharField(max_length=3, default='N', blank=True)

    first_name = models.CharField(max_length=100, blank=True)
    second_name = models.CharField(max_length=100, blank=True)
    first_surname = models.CharField(max_length=100, blank=True)
    second_surname = models.CharField(max_length=100, blank=True)
    
    def get_full_name(self):
        return f"{self.name} {self.first_name} {self.second_name} {self.first_surname} {self.second_surname}".strip()
    
    def __str__(self):
        if self.name and len(self.name) > 0:
            return self.name
        
        return self.get_full_name()
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['name']