from django.urls import path, include
from .views import *
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Datak E-commerce API",
      default_version='v1',
      description="",
      contact=openapi.Contact(email="daniel@datak.co"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register("products", ProductViewSet)
router.register("emailSubscriptions", EmailSubscriptionViewSet)
router.register("orders", OrderViewSet)
router.register("orderItems", OrderItemViewSet)
router.register("orderGroups", OrderGroupViewSet)
router.register("commerce", CommerceViewSet)
router.register("commercePublic/products", ProductAvailableView, basename="productAvailable")
router.register("commercePublic/categories", PublicCategoryViewSet, basename="publicCategory")
router.register("customers", CustomerViewSet)
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("productAttributes", ProductAttributeViewSet)
router.register("attributeOptions", AttributeOptionViewSet)
router.register("attributeValues", AttributeValueViewSet)


urlpatterns = [
    path('', schema_view.with_ui(cache_timeout=0), name='openapi-ui'),
    path('openapi', schema_view.without_ui(cache_timeout=0), name='openapi-schema'),
    path("v1/", include(router.urls)),
    path("v1/commercePublic/orders/<int:id>/", OrderPublicAPIView.as_view()),
    path("v1/commercePublic/commerce/<int:id>/", CommercePublicAPIView.as_view()),
    path("v1/commercePublic/orderPlacement/", OrderPlacementAPIView.as_view()),
    path("v1/commercePublic/orderPayment/<int:id>/", OrderPaymentAPIView.as_view()),
    path("v1/commercePublic/orderAddiPayment/<int:id>/", OrderAddiPaymentAPIView.as_view()),
    path("v1/commercePublic/addiCallback", AddiCallbackAPIView.as_view()),
    path("v1/commercePublic/sendEmail", SendEmailView.as_view())
]
