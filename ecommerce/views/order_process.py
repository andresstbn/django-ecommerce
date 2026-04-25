from rest_framework import generics, serializers, status, views, response, permissions
from ecommerce.models import Order, Customer, OrderItem, Coupon, OrderGroup, Commerce
from ecommerce.serializers import OrderSerializer
import mercadopago
import requests
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from utils.mails import send_order_placement_mail
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import base64
import json
from django.conf import settings

class ProductPlacementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    qty = serializers.IntegerField()
    size = serializers.CharField()


class OrderPlacementSerializer(serializers.Serializer):
    delivery = serializers.CharField(default="paid", required=False)
    municipality = serializers.CharField()
    department = serializers.CharField()
    address = serializers.CharField()
    phone = serializers.CharField()
    email = serializers.CharField()
    name = serializers.CharField()
    document_number = serializers.CharField()
    last_name = serializers.CharField()
    discountCode = serializers.CharField(required=False)
    products = ProductPlacementSerializer(many=True)
    commerce = serializers.PrimaryKeyRelatedField(queryset=Commerce.objects.all())


class OrderPlacementAPIView(generics.GenericAPIView):
    serializer_class = OrderPlacementSerializer

    def get_coupon(self, discountCode):
        try:
            if discountCode and Coupon.objects.filter(code=discountCode).exists():
                return Coupon.objects.get(code=discountCode)
        except Exception as e:
            print("Error al buscar el cupón", e)

        return None

    @swagger_auto_schema(
        request_body=OrderPlacementSerializer, responses={200: OrderSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.commerce = data["commerce"]
        discounts_dict = self.commerce.get_discounts()

        global_discount_dict = discounts_dict.get("global_discount", {})
        min_qty_discount_dict = discounts_dict.get("min_qty_discount", {})

        global_discount_percentage_enabled = (
            int(global_discount_dict.get("percentage", 0) or "0") > 0
        )
        min_qty_discount_percentage_enabled = (
            int(min_qty_discount_dict.get("percentage", 0) or "0") > 0
        )
        coupon_discount_enabled = discounts_dict.get("coupon_discount", {}).get(
            "value", False
        )

        if min_qty_discount_percentage_enabled or global_discount_percentage_enabled:
            coupon_discount_enabled = False

        if min_qty_discount_percentage_enabled:
            global_discount_percentage_enabled = False
        customer = Customer.objects.create(
            name=data["name"],
            last_name = data["last_name"],
            address=data["address"],
            phone_number=data["phone"],
            email=data["email"],
            document_number=data["document_number"],
            municipality=data["municipality"],
            department=data["department"],
            commerce=data["commerce"],
        )

        order = Order(customer=customer, commerce=data["commerce"])
        order.save()

        for product in data["products"]:
            order_item = OrderItem.objects.create(
                order=order,
                product_id=product["id"],
                quantity=product["qty"],
                variant_raw=product["size"],
            )

        for item in order.items.all():
            item.price = item.product.price
            item.save(update_fields=["price"])
            
            if item.product.discount_percentage > 0:
                product_price = float(item.product.price)
                product_discount_percentage = float(item.product.discount_percentage)
                product_discount_amount = product_price * (
                    product_discount_percentage / 100.0
                )
                order.discount_amount += product_discount_amount

        order.subtotal_amount = float(order.total_amount())
        ## TODO: Esto se desactivo para dejar los descuentos por item funcionales: Revisar el modelo de order tbn al descomentar
        # if coupon_discount_enabled: 
        #     coupon = self.get_coupon(data.get("discountCode", None))
        #     coupon_subscription = None
        #     try:
        #         coupon_subscription = coupon.subscription
        #     except:
        #         pass

        #     if coupon:
        #         if (coupon_subscription and not coupon.order) or (
        #             not coupon_subscription
        #         ):
        #             coupon.order = order
        #             coupon.save()
        #             order.discount_amount = (float(coupon.discount) / 100.0) * float(
        #                 order.subtotal_amount
        #             )

        # if global_discount_percentage_enabled:
        #     order.discount_amount = (
        #         float(global_discount_dict.get("percentage", 0)) / 100.0
        #     ) * float(order.subtotal_amount)

        # if min_qty_discount_percentage_enabled:
        #     min_qty_discount = discounts_dict.get("min_qty_discount", {})
        #     min_qty = int(min_qty_discount.get("min_qty", 0) or "0")
        #     percentage = float(min_qty_discount.get("percentage", 0) or "0")
        #     total_articles = sum([item.quantity for item in order.items.all()])

        #     if total_articles >= min_qty:
        #         articles_to_discount = total_articles - min_qty + 1
        #         cheaper_items = sorted(order.items.all(), key=lambda x: x.price)[
        #             :articles_to_discount
        #         ]
        #         order.discount_amount = sum(
        #             [float(item.price) for item in cheaper_items]
        #         ) * (percentage / 100.0)

        order.amount = float(order.subtotal_amount) - float(order.discount_amount)
        print("Order amount", order.amount, order.subtotal_amount, order.discount_amount)
        
        
        if data.get("delivery", "paid") == "paid":
            order.extra_amounts = [
                {
                    "type": "shipping",
                    "name": "Envío",
                    "amount": 16500,
                }
            ]
            order.amount += 16500

        order.save(
            update_fields=[
                "subtotal_amount",
                "discount_amount",
                "amount",
                "extra_amounts",
            ]
        )
        return response.Response(OrderSerializer(order).data)


class OrderPaymentSerializer(serializers.Serializer):
    payment_method = serializers.CharField()
    payment_data = serializers.JSONField()


class OrderPaymentAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(request_body=OrderPaymentSerializer)
    def post(self, request, **kwargs):
        serializer = OrderPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = Order.objects.get(id=kwargs["id"])
        payment_method = data.get("payment_method")
        input_payment_data = data.get("payment_data")
        payer = input_payment_data.get("payer")
        identification = payer.get("identification")
        mercadopago_public_key = order.commerce.payment_public_key
        mercadopago_access_token = order.commerce.payment_access_token
        sdk = mercadopago.SDK(mercadopago_access_token)

        payment_data = {
            "transaction_amount": float(input_payment_data.get("transaction_amount")),
            "token": input_payment_data.get("token"),
            "description": input_payment_data.get("description"),
            "installments": int(input_payment_data.get("installments")),
            "payment_method_id": input_payment_data.get("payment_method_id"),
            "payer": {
                "email": order.customer.email,
                "first_name": order.customer.name,
                "identification": {
                    "type": identification.get("type"),
                    "number": identification.get("number"),
                },
            },
        }

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        order.payment_details = {
            "request": payment_data,
            "response": payment,
        }

        order.payment_success = payment.get("status", "") == "approved"

        order.payment_datetime = payment.get("date_created", "")
        fields = ["payment_details", "payment_success"]
        if order.payment_success:
            fields.append("payment_datetime")

        order.save(update_fields=fields)

        try:
            send_order_placement_mail(order)
        except Exception as e:
            print("Error enviando el mail de confirmación")

        return response.Response(payment)




class OrderAddiPaymentSerializer(serializers.Serializer):
    client_data = serializers.JSONField()
    payment_data = serializers.JSONField()
    

class OrderAddiPaymentAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def addi_auth_api(request, client_data):
        url = settings.ADDI_AUTH_API
        payload = client_data
        response = requests.post(url, json=payload)
        data = response.json()
        return data
    
    def addi_payment_api(request, payment_data, token):
        url = settings.ADDI_PAYMENT_API
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = payment_data
        response = requests.post(url, json=payload, headers=headers)
        
        data = response.url
        
        return data

    @swagger_auto_schema(request_body=OrderAddiPaymentSerializer)
    def post(self, request, **kwargs):
        serializer = OrderAddiPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order = Order.objects.get(id=kwargs["id"])
        input_client_data = data.get("client_data")
        input_payment_data = data.get("payment_data")
        auth_response = self.addi_auth_api(input_client_data)
        token = auth_response.get("access_token")
        payment_response = self.addi_payment_api(input_payment_data, token)
        #print("HERE", settings.ADDI_WEBHOOK_USERNAME)
        return Response({"location": payment_response}, status=status.HTTP_200_OK)
        
        
        
class AddiCallbackAPIView(views.APIView):
    """
    API para recibir notificaciones de Addi con autenticación básica
    y actualizar el estado de la orden en la base de datos.
    """

    @method_decorator(csrf_exempt)  # Desactiva la verificación CSRF para esta vista
    def post(self, request, *args, **kwargs):
        # 1️⃣ Verificar autenticación básica
        if not self.authenticate(request):
            return Response({"error": "No autorizado"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # 2️⃣ Obtener los datos del webhook
            data = json.loads(request.body)

            order_id = data.get("orderId")
            application_id = data.get("applicationId")
            approved_amount = float(data.get("approvedAmount", 0))
            currency = data.get("currency")
            status_addi = data.get("status")
            status_timestamp = data.get("statusTimestamp")

            # 3️⃣ Buscar la orden en la base de datos
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({"error": "Orden no encontrada"}, status=status.HTTP_404_NOT_FOUND)

            # 4️⃣ Actualizar estado de la orden en función del estado recibido
          
            order.payment_details = {
                "addi_application_id": application_id,
                "addi_status": status_addi,
                "approved_amount": approved_amount,
                "currency": currency,
                "status_timestamp": status_timestamp,
            }
            order.payment_success = status_addi == "APPROVED"
            order.payment_datetime = status_timestamp if status_addi == "APPROVED" else None
            order.save()

            return Response({"message": "Webhook procesado correctamente"}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({"error": "JSON inválido"}, status=status.HTTP_400_BAD_REQUEST)

    def authenticate(self, request):
        """
        Verifica la autenticación básica en la cabecera Authorization.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False

        # Obtener credenciales en Base64
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)

        # Validar credenciales con las almacenadas en el servidor
        expected_username = settings.ADDI_WEBHOOK_USERNAME
        expected_password = settings.ADDI_WEBHOOK_PASSWORD

        return username == expected_username and check_password(password, expected_password)