from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from ecommerce.models import Commerce
from ecommerce.serializers import CommerceSerializer

class CommerceRelatedViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    def get_commerce_id(self):
        if self.request.headers.get("X-Commerce-Id", None):
            return self.request.headers.get("X-Commerce-Id")
        if self.request.query_params.get("commerce", None):
            return self.request.query_params.get("commerce")
        
        return None
    
    def create(self, request, *args, **kwargs):
        commerce_id = self.get_commerce_id()
        if commerce_id:
            request.data["commerce"] = commerce_id
        return super().create(request, *args, **kwargs)
    
    def get_queryset(self):
        commerce_id = self.get_commerce_id()
        if commerce_id:
            return self.queryset.filter(commerce=commerce_id)
        
        return self.queryset