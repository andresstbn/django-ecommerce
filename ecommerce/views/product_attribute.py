from ecommerce.views.common import CommerceRelatedViewSet
from ecommerce.models import ProductAttribute, AttributeValue, AttributeOption
from ecommerce.serializers import ProductAttributeSerializer, AttributeValueSerializer, AttributeOptionSerializer
from rest_framework import viewsets

class ProductAttributeViewSet(CommerceRelatedViewSet):
    serializer_class = ProductAttributeSerializer
    queryset = ProductAttribute.objects.all()

class AttributeOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeOptionSerializer
    queryset = AttributeOption.objects.all()
    filterset_fields = ['attribute']

class AttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = AttributeValueSerializer
    queryset = AttributeValue.objects.all()
    filterset_fields = ['product', 'attribute_options']