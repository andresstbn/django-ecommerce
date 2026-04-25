from ecommerce.views.common import CommerceRelatedViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ecommerce.models import EmailSubscription, Coupon
from ecommerce.serializers import EmailSubscriptionSerializer
from rest_framework.decorators import action
from utils.mails import send_subscription_mail
class EmailSubscriptionViewSet(CommerceRelatedViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EmailSubscriptionSerializer
    queryset = EmailSubscription.objects.all()
    
    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, **kwargs):
        email_subscription = self.get_object()
        email_subscription.is_active = False
        email_subscription.save()
        return Response({"success": True, "message": "Email subscription has been deactivated."})
    
    @action(detail=True, methods=["post"])
    def subscribe(self, request, **kwargs):
        email_subscription = self.get_object()
        email_subscription.is_active = True
        email_subscription.save()
        return Response({"success": True, "message": "Email subscription has been activated."})

    @action(detail=False, methods=["post"])
    def subscribe(self, request, **kwargs):
        data = request.data
        email = data.get("email")
        commerce = data.get("commerce")
        
        if not email:
            return Response({"success": False, "message": "Email is required."})
                            
        if EmailSubscription.objects.filter(email=email, commerce=commerce).exists():
            return Response({"success": False, "message": "Email is already subscribed."})
                            
        coupon = Coupon.objects.create(commerce_id=commerce, discount=15)
        email_subscription = EmailSubscription.objects.create(email=email, verification_coupon=coupon, commerce_id=commerce)
        send_subscription_mail(email, coupon.code)
        return Response({"success": True, "message": "Email subscription has been activated."})
    