from rest_framework import generics, viewsets, permissions, decorators, response, serializers, parsers
from ecommerce.models import Product, Category
from ecommerce.serializers import ProductSerializer, ProductAvailableSerializer, ProductImageSerializer
from ecommerce.views.common import CommerceRelatedViewSet
from drf_yasg.utils import swagger_auto_schema
from django.core.files import File


class ProductAvailableView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProductAvailableSerializer
    queryset = Product.objects.filter(published=True).with_catalog_data()
    filterset_fields = ['commerce']
    
class UpdateCategoriesSerializer(serializers.Serializer):
    categories = serializers.ListField(child=serializers.IntegerField())
    new_categories = serializers.ListField(child=serializers.CharField())
    
class UploadImageSerializer(serializers.Serializer):
    image = serializers.ImageField()
    
class UpdateImagesSerializer(serializers.Serializer):
    delete_images = serializers.ListField(child=serializers.IntegerField(), required=False)
    reorder_images = serializers.ListField(child=serializers.IntegerField(), required=False)
    
class ProductViewSet(CommerceRelatedViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProductSerializer
    queryset = Product.objects.with_catalog_data()
    
    @swagger_auto_schema(request_body=UploadImageSerializer)
    @decorators.parser_classes([parsers.FormParser, parsers.MultiPartParser])
    @decorators.action(detail=True, methods=["post"])
    def upload_image(self, request, **kwargs):    
        serializer = UploadImageSerializer(data=request.data)
        serializer.is_valid()
        product = self.get_object()
        image_file = serializer.validated_data.get("image", None)
        
        if not image_file:
            return response.Response({"error": "No image file provided"}, status=400)
        
        product_image = product.images.create(image=image_file)
        serializer_response = ProductImageSerializer(product_image)
        return response.Response(serializer_response.data)
    
    @swagger_auto_schema(request_body=UpdateImagesSerializer)
    @decorators.action(detail=True, methods=["post"])
    def update_images(self, request, **kwargs):
        serializer = UpdateImagesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.get_object()
        data = serializer.validated_data
        delete_images = data.get("delete_images", [])
        reorder_images = data.get("reorder_images", [])
        
        for image_id in delete_images:
            product.images.get(id=image_id).delete()
            
        for k, image_id in enumerate(reorder_images):
            product.images.filter(id=image_id).update(order_index=k)
            
        return response.Response(ProductSerializer(product).data)
    
    @swagger_auto_schema(request_body=UpdateCategoriesSerializer)
    @decorators.action(detail=True, methods=["post"])
    def update_categories(self, request, **kwargs):
        serializer = UpdateCategoriesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = self.get_object()
        data = serializer.validated_data
        existing_categories = data.get("categories", [])
        new_categories = data.get("new_categories", [])
        
        for category in new_categories:
            cat = Category.objects.get_or_create(name=category, commerce=product.commerce)
            existing_categories.append(cat[0].id)
            
        product.categories.set(existing_categories)
        return response.Response(ProductSerializer(product).data)
    
    

