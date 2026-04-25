from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings


class CommerceLayout(models.Model):
    commerce = models.OneToOneField("Commerce", on_delete=models.CASCADE)


def get_path_commerce(instance, filename):
    word = "dev" if settings.ENV == "DEVELOPMENT" else "prod"
    return f"ecommerce/{word}/commerce_images/{instance.id}/{filename}"


def get_path_commerce_image(instance, filename):
    word = "dev" if settings.ENV == "DEVELOPMENT" else "prod"
    return f"ecommerce/{word}/commerce_images/{instance.commerce.id}/{filename}"


def get_default_social_networks():
    return {
        "facebook": {
            "url": "",
            "enabled": False,
        },
        "instagram": {
            "url": "",
            "enabled": False,
        },
        "twitter": {
            "url": "",
            "enabled": False,
        },
        "youtube": {
            "url": "",
            "enabled": False,
        },
        "whatsapp": {
            "number": "",
            "enabled": False,
        },
    }


def get_default_settings():
    return {
        "discounts": [
            {
                "name": "global_discount",
                "label": "Descuento general",
                "value": False,
                "amount": 0,
                "end_date": "",
                "min_amount": 0,
                "percentage": 0,
                "start_date": "",
                "description": "Se aplicará sobre el total de los pedidos del Ecommerce",
                "usage_limits": "",
                "marked_products": False,
            },
            {
                "name": "min_qty_discount",
                "min_qty": 0,
                "value": False, 
                "description": "Se aplicará sobre el total de los pedidos del Ecommerce si se cumple con la cantidad mínima",
            },
            {
                "name": "category_discount",
                "label": "Descuento por categoría",
                "cateogories": [],
                "value": False, 
                "percentage": 0,
                "description": "Se aplicará sobre los productos de las categorías seleccionadas",
            },
            {
                "name": "subscription_discount",
                "label": "Descuento Suscripción",
                "value": False,
                "amount": 0,
                "end_date": "",
                "percentage": 0,
                "start_date": "",
                "description": "Se aplicará sobre los pedidos con cupon de suscripción",
            },
            {
                "name": "selected_products_discount",
                "label": "Descuento Producto seleccionados",
                "value": False,
                "amount": 0,
                "end_date": "",
                "products": [],
                "min_amount": 0,
                "percentage": 0,
                "start_date": "",
                "description": "Se aplicará sobre productos del Ecommerce",
                "usage_limits": "",
                "marked_products": False,
            },
            {
                "name": "coupon_discount",
                "label": "Descuento cupon",
                "value": False,
                "coupons": [],
                "description": "Se aplicará sobre los pedidos con cupon",
            },
        ],
        "notifications": [
            {
                "name": "order_send_email",
                "label": "Enviar email de pedido",
                "value": True,
            },
            {
                "name": "payment_confirmation_email",
                "label": "Enviar email confirmación pago",
                "value": True,
            },
            {
                "name": "shipping_email",
                "label": "Enviar email de datos de envio",
                "value": True,
            },
            {
                "name": "suscription_email",
                "label": "Enviar email de suscripción",
                "value": True,
            },
        ],
        "shipping": [
            {"name": "COD_shipping", "label": "Contra entrega", "value": False},
            {
                "name": "general_shipping",
                "label": "General",
                "value": False, # TODO: Change "value" to "enabled"
                "amount": 0,
                "max_time": 0,
                "min_time": 0,
                "free_limit": 0,
            },
            {
                "name": "customed_shipping",
                "label": "Personalizados",
                "value": False, # TODO: Change "value" to "enabled"
                "locations": [],
            },
        ],
    }


def get_default_text_fields():
    return {
        "whatsapp_share_message": "¡Hola! Estoy interesado",
    }


class Commerce(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    published = models.BooleanField(default=False, verbose_name="Publicado")
    settings = models.JSONField(
        default=get_default_settings, verbose_name="Configuración", blank=True
    )
    is_tailormade = models.BooleanField(
        default=False, verbose_name="¿Es un sitio hecho a medida?"
    )
    text_fields = models.JSONField(
        default=get_default_text_fields, verbose_name="Campos de texto", blank=True
    )
    site_customizations = models.JSONField(
        default=dict, verbose_name="Personalizaciones", blank=True
    )

    subdomain = models.CharField("Subdominio", max_length=100, blank=True, default="")

    ## Campos sobre proveedor de pagos
    PAYMENT_PROVIDERS = [
        ("mercadopago", "mercadopago"),
        ("wompi", "wompi"),
        ("epayco", "epayco"),
    ]
    payment_provider = models.CharField(
        max_length=100,
        choices=PAYMENT_PROVIDERS,
        verbose_name="Proveedor de pagos",
        blank=True,
    )
    payment_public_key = models.CharField(
        max_length=100, verbose_name="Llave pública", blank=True
    )
    payment_access_token = models.CharField(
        max_length=100, verbose_name="Token de acceso", blank=True
    )

    ## Campos sobre notificaciones
    notification_emails = ArrayField(
        base_field=models.EmailField(),
        verbose_name="Correos de notificación",
        blank=True,
        default=list,
    )
    favicon = models.ImageField(
        upload_to=get_path_commerce, verbose_name="Favicon", blank=True, null=True
    )
    logo = models.ImageField(
        upload_to=get_path_commerce, verbose_name="Logo", blank=True, null=True
    )

    ## Campos de RRSS
    social_networks = models.JSONField(
        default=get_default_social_networks, verbose_name="Redes sociales", blank=True
    )

    description = models.TextField(default="", verbose_name="Descripción", blank=True)
    phone_number = models.CharField(
        max_length=100, verbose_name="Número de teléfono", blank=True
    )
    address = models.CharField(max_length=100, verbose_name="Dirección", blank=True)
    location = models.CharField(max_length=100, verbose_name="Ubicación", blank=True)

    def __str__(self):
        return self.name
    
    def get_discount_by_name(self, name, only_enabled=True):
        if only_enabled:
            discounts = self.get_enabled_discounts()
        else:
            discounts = self.settings.get("discounts", [])
        return next((d for d in discounts if d.get("name") == name), None)
    
    def get_enabled_discounts(self):
        discounts = self.settings.get("discounts", [])
        return [d for d in discounts if d.get("value", False)]
    
    def get_discounts(self):
        POSSIBLE_DISCOUNTS = ["global_discount", "category_discount", "min_qty_discount", "coupon_discount"]
        FIELDS = {
            'global_discount': ['amount', 'percentage'],
            'category_discount': ['amount', 'percentage', 'categories'],
            'min_qty_discount': ['amount', 'percentage', 'mode', 'min_qty'],
            'coupon_discount': ['value']
        }
        discounts_dict = {}

        for name in POSSIBLE_DISCOUNTS:
            discount_dict = self.get_discount_by_name(name)
            if not discount_dict:
                continue
            discounts_dict[name] = { field: discount_dict.get(field, '')  for field in FIELDS[name] }
            
        return discounts_dict 

    class Meta:
        verbose_name = "Comercio"
        verbose_name_plural = "Comercios"


class CommerceImage(models.Model):
    commerce = models.ForeignKey(
        "Commerce", on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to=get_path_commerce_image, verbose_name="Imagen")
    identifier = models.CharField(
        max_length=100, verbose_name="Identificador", blank=True
    )
    styles = models.JSONField(default=dict, verbose_name="Estilos", blank=True)

    def __str__(self):
        return f"{self.commerce.name} - {self.order}"

    class Meta:
        verbose_name = "Imagen de comercio"
        verbose_name_plural = "Imágenes de comercio"
