from django.db import models
from ecommerce.models.product_attribute import AttributeOption
from django.core.validators import MinValueValidator, MaxValueValidator

def get_default_extra_amounts():
    return {
        "shipping": {
            "type": "shipping",
            "name": "Envío",
            "amount": 0,
        }
    }


def get_default_packaging():
    return {
        "packedge": "",
        "weight": 0,
        "length": 0,
        "width": 0,
        "height": 0,
        "depth": 0,
    }


def get_default_taxes():
    return {
        "iva": {
            "label": "IVA",
            "option": {
                "label": "Excluido",
                "value": 0,
            },
        },
        "iva_purchase": {
            "label": "IVA compra",
            "option": {
                "label": "Excluido",
                "value": 0,
            },
        },
        "inc_sales": {
            "label": "Imp. consumo ventas",
            "option": {"label": "", "percentage": 0, "amount": 0},
        },
        "inc_purchases": {
            "label": "Imp. consumo compras",
            "option": {"label": "", "percentage": 0, "amount": 0},
        },
    }


class ProductQuerySet(models.QuerySet):
    def with_catalog_data(self):
        return self.prefetch_related(
            "images",
            "categories",
            models.Prefetch(
                "attributevalue_set__attribute_options",
                queryset=AttributeOption.objects.select_related("attribute"),
            ),
        )


class Product(models.Model):
    objects = ProductQuerySet.as_manager()
    ARTICLE_TYPE_CHOICES = [("I", "Inventario"), ("S", "Servicio")]
    commerce = models.ForeignKey("Commerce", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=50, default="", blank=True, verbose_name="Código"
    )
    starred = models.BooleanField(default=False)
    description = models.TextField(default="", blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    currency = models.CharField(
        max_length=3, default="COP", choices=[("COP", "COP"), ("USD", "USD")]
    )
    creation_datetime = models.DateTimeField(auto_now_add=True)
    last_update_datetime = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    article_type = models.CharField(
        max_length=50, choices=ARTICLE_TYPE_CHOICES, default="I"
    )

    categories = models.ManyToManyField("Category", related_name="products", blank=True)
    cost_price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    brand = models.ForeignKey("Brand", on_delete=models.CASCADE, blank=True, null=True, default=None, related_name="products")
    barcode = models.CharField(max_length=50, verbose_name="Código de barras", blank=True)
    reference = models.CharField(max_length=50, verbose_name="Referencia", blank=True)
    unit = models.CharField(max_length=50, verbose_name="Unidad", blank=True, default="")
    taxes = models.JSONField(default=get_default_taxes, blank=True)
    packaging = models.JSONField(default=get_default_packaging, blank=True)
    extra_amounts = models.JSONField(default=get_default_extra_amounts, blank=True)
    product_type = models.CharField(max_length=5, verbose_name="Tipo de producto", default="PF", blank=True)
    layout_settings = models.JSONField(default=dict, blank=True)
    discount_percentage = models.DecimalField(decimal_places=2, max_digits=5, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def get_stock(self):
        return sum(value.stock for value in self.attributevalue_set.all())

    def get_attribute_values(self):
        """{attribute: {option: stock}}. Uses prefetched rows (see Product.objects.with_catalog_data)."""
        options = {}
        stock_by_option = {}
        for value in self.attributevalue_set.all():  # ordered by -id: first match wins, as before
            for option in value.attribute_options.all():
                options[option.id] = option
                stock_by_option.setdefault(option.id, value.stock)

        return_dict = {}
        for option_id in sorted(options, reverse=True):  # AttributeOption ordering is -id
            option = options[option_id]
            return_dict.setdefault(option.attribute.name, {})[option.name] = stock_by_option[option_id]
        return return_dict

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-id"]
