from rest_framework import viewsets, permissions, generics
from ecommerce.models import Commerce
from ecommerce.serializers import CommerceSerializer, CommercePublishedSerializer

class CommerceViewSet(viewsets.ModelViewSet):
    serializer_class = CommerceSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Commerce.objects.all()

class CommercePublicAPIView(generics.RetrieveAPIView):
    queryset = Commerce.objects.all()
    serializer_class = CommercePublishedSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"