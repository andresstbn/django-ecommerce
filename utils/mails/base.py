from google.appengine.api import mail

SENDER_EMAIL = "noreply@datak.co"

def send_email(subject, recipient_list, body, bcc):
    try:
        message = mail.EmailMessage(
            sender=SENDER_EMAIL,
            to=recipient_list,
            subject=subject,
            bcc=bcc,
            html=body,
        )
        message.check_initialized()
        message.send()

    except Exception as e:
        print(e)
        return False