from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ecommerce.models import Category, Brand
from ecommerce.serializers import CategorySerializer, BrandSerializer
from ecommerce.views.common import CommerceRelatedViewSet


class CategoryViewSet(CommerceRelatedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("parent", "name", "commerce")
    search_fields = ("name",)
    
class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = ()
    filterset_fields = ("parent", "name", "commerce")
    search_fields = ("name",)
    

class BrandViewSet(CommerceRelatedViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ("name", "commerce")
    search_fields = ("name",)
    
