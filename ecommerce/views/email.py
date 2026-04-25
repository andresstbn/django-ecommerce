from rest_framework import permissions, views, serializers, response, status
from google.appengine.api import mail
from drf_yasg.utils import swagger_auto_schema
SENDER_EMAIL = "noreply@datak.co"

def send_email(subject, recipient_list, body, cc=None, bcc=None):
    try:
        kwargs = {
            "sender": SENDER_EMAIL,
            "to": recipient_list,
            "subject": subject,
            "html": body,
        }

        if cc:
            kwargs["cc"] = cc
        if bcc:
            kwargs["bcc"] = bcc

        message = mail.EmailMessage(**kwargs)
        message.check_initialized()
        message.send()
        return True

    except Exception as e:
        print(e)
        print("Mocking email sending")
        return False


class SendEmailSerializer(serializers.Serializer):
    subject = serializers.CharField()
    recipient_list = serializers.ListField(child=serializers.EmailField())
    body = serializers.CharField()
    bcc = serializers.ListField(child=serializers.EmailField(), required=False)
    cc = serializers.ListField(child=serializers.EmailField(), required=False)


class SendEmailView(views.APIView):
    # permission_classes = (permissions.IsAuthenticated,) // TODO: Uncomment this line
    @swagger_auto_schema(request_body=SendEmailSerializer)
    def post(self, request, *args, **kwargs):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        send_email(**serializer.validated_data)
        return response.Response(
            {"message": "Email sent successfully"}, status=status.HTTP_200_OK
        )
