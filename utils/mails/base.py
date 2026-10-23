import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_email(subject, recipient_list, body, bcc=None, cc=None):
    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list,
            bcc=bcc or [],
            cc=cc or [],
        )
        message.content_subtype = "html"
        message.send()
        return True

    except Exception:
        logger.exception("Error sending email %r to %s", subject, recipient_list)
        return False
