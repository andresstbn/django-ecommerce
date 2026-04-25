from rest_framework import serializers

from ecommerce.models import (
    Order,
    OrderGroup,
    Product,
    Customer,
    ProductImage,
    EmailSubscription,
    OrderItem,
    Category,
    Brand,
    Commerce,
)


class CategorySerializer(serializers.ModelSerializer):
    is_erasable = serializers.ReadOnlyField(source="get_is_erasable")

    class Meta:
        model = Category
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):
    is_erasable = serializers.ReadOnlyField(source="get_is_erasable")

    class Meta:
        model = Brand
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.ReadOnlyField()
    product_name = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderGroup
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    # customer = CustomerSerializer(read_only=True) // Quitado por solicitud de front.
    total_amount = serializers.ReadOnlyField()
    prefix = serializers.ReadOnlyField(source="group.prefix")
    customer_full_name = serializers.ReadOnlyField(source="customer.get_full_name")
    customer_email = serializers.ReadOnlyField(source="customer.email")

    class Meta:
        model = Order
        fields = "__all__"


class OrderForPaymentSerializer(OrderSerializer):
    customer = CustomerSerializer(read_only=True)  # Quitado por solicitud de front.
    public_key = serializers.ReadOnlyField(source="commerce.payment_public_key")

    class Meta:
        model = Order
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("image", "thumbnail", "id")


class ProductAvailableSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    attribute_values = serializers.ReadOnlyField(source="get_attribute_values")
    price_with_discount = serializers.SerializerMethodField()
    
    
    
    def get_price_with_discount(self, obj):
        return obj.price - (obj.price * obj.discount_percentage / 100)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "currency",
            "published",
            "images",
            "attribute_values",
            "starred",
            "categories",
            "discount_percentage",
            "price_with_discount",
        )


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    total_stock = serializers.ReadOnlyField(source="get_stock")
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class CommerceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commerce
        fields = "__all__"


class CommercePublishedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commerce
        fields = ("settings", "text_fields", "favicon", "logo")


class EmailSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSubscription
        fields = "__all__"
