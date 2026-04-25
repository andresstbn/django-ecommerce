from rest_framework import serializers
from ecommerce.models import ProductAttribute, AttributeValue, AttributeOption



class AttributeOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeOption
        fields = "__all__"
        
class ProductAttributeSerializer(serializers.ModelSerializer):
    options = AttributeOptionSerializer(many=True, read_only=True)
    class Meta:
        model = ProductAttribute
        fields = "__all__"
        
class AttributeValueSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    attribute_option_names = serializers.ReadOnlyField(source="get_attribute_option_names")
    
    class Meta:
        model = AttributeValue
        fields = "__all__"