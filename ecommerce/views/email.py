from rest_framework import permissions, views, serializers, response, status
from drf_yasg.utils import swagger_auto_schema
from utils.mails.base import send_email


class SendEmailSerializer(serializers.Serializer):
    subject = serializers.CharField()
    recipient_list = serializers.ListField(child=serializers.EmailField())
    body = serializers.CharField()
    bcc = serializers.ListField(child=serializers.EmailField(), required=False)
    cc = serializers.ListField(child=serializers.EmailField(), required=False)


class SendEmailView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    @swagger_auto_schema(request_body=SendEmailSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_email(**serializer.validated_data)
        return response.Response(
            {"message": "Email sent successfully"}, status=status.HTTP_200_OK
        )
