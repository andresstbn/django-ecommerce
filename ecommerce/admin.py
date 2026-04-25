from django.contrib import admin
from ecommerce.models import *
from django_json_widget.widgets import JSONEditorWidget

admin.site.site_header = "Datak e-commerce"
admin.site.site_title = "Admin"
admin.site.index_title = "Datak"


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class AttributeValueInline(admin.StackedInline):
    def has_add_permission(self, request, *args, **kwargs):
        return False

    exclude = ("attribute_options",)
    model = AttributeValue


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("name", "phone_number", "address", "orders_qty")

    def orders_qty(self, instance):
        return instance.orders.count()


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("code", "discount", "active", "subscription")


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(OrderGroup)
class OrderGroupAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("name", "prefix", "commerce")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("commerce", "name", "parent", "is_erasable", "settings")
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    def is_erasable(self, instance):
        return instance.get_is_erasable()


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("commerce", "name", "is_erasable")
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }

    def is_erasable(self, instance):
        return instance.get_is_erasable()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "customer",
        "commerce",
        "creation_datetime",
        "payment_success",
        "discount_amount",
        "discount_percentage",
        "subtotal_amount",
        "total_amount",
    )
    inlines = [OrderItemInline]
    list_filter = ("payment_success", "commerce")
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }
    search_fields = ("customer__name", "customer__phone_number")

    def discount_percentage(self, instance):
        if instance.discount_amount == 0:
            return "-"

        return f"{100*(instance.discount_amount/instance.subtotal_amount)}%"


@admin.register(EmailSubscription)
class EmailSubscriptionAdmin(admin.ModelAdmin):
    list_filter = ("commerce",)
    list_display = ("email", "commerce", "creation_datetime", "coupon_code")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    actions = ["publish", "unpublish", "star", "unstar", "set_discount_30", "set_discount_50"]
    list_filter = ("commerce",)
    list_display = (
        "name",
        "price",
        "commerce",
        "published",
        "images_qty",
        "starred",
        "discount_percentage",
    )
    inlines = [AttributeValueInline, ProductImageInline]

    def star(self, request, queryset):
        queryset.update(starred=True)

    def unstar(self, request, queryset):
        queryset.update(starred=False)

    def publish(self, request, queryset):
        queryset.update(published=True)

    def unpublish(self, request, queryset):
        queryset.update(published=False)

    def images_qty(self, instance):
        return instance.images.count()

    def set_discount_30(self, request, queryset):
        queryset.update(discount_percentage=30)

    def set_discount_50(self, request, queryset):
        queryset.update(discount_percentage=50)

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(Commerce)
class CommerceAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "get_discounts")
    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget},
    }


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "commerce")
    list_filter = ("commerce",)
    inlines = [AttributeOptionInline]
