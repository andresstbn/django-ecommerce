from ecommerce.views.common import CommerceRelatedViewSet
from ecommerce.models import Customer
from ecommerce.serializers import CustomerSerializer

class CustomerViewSet(CommerceRelatedViewSet):
    search_fields = ["first_name", "second_name", "first_surname", "second_surname"]
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    