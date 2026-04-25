from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, viewsets
from ecommerce.models import Order, Customer, OrderItem, Coupon, OrderGroup, OrderItem
from ecommerce.serializers import OrderSerializer, OrderGroupSerializer, OrderForPaymentSerializer, OrderItemSerializer
from ecommerce.views.common import CommerceRelatedViewSet
import logging

logger = logging.getLogger(__name__)
    
class OrderGroupViewSet(CommerceRelatedViewSet):
    serializer_class = OrderGroupSerializer
    queryset = OrderGroup.objects.all()
    permission_classes = (IsAuthenticated,)


class OrderPublicAPIView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderForPaymentSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"


class OrderViewSet(CommerceRelatedViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated,)
    filterset_fields = ['payment_success']
    

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    queryset = OrderItem.objects.all()
    filterset_fields = ['order']
    permission_classes = (IsAuthenticated,)