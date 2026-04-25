from google.appengine.api import mail
from django.template.loader import get_template
from .base import send_email

def get_body(email, code):
    return f"""<strong>
            <span style="color:#837A63">Hola, {email}</span> 
            <br>
            <br>
            <span style="color:#837A63">
                Es un placer darte la bienvenida a nuestro
                boletín informativo y agradecemos sinceramente que te hayas suscrito. Nos complace que formes parte de
                nuestra familia y queremos mostrar nuestro agradecimiento desde el primer momento.
            </span>
            <br>
            <br>

            <span style="color:#837A63">
                Para expresar nuestra gratitud, hemos preparado un bono del 15% de descuento exclusivo para ti.
            </span>
            </strong>
            <br>
            <h3>Código descuento: {code}</h3>
            <span>
                Redime el siguiente codigo en tu proxima compra.
            </span>"""


def send_subscription_mail(email, code):
    subject = "Bienvenido a Cuora!"
    recipient_list = [email]
    
    template = get_template("ecommerce/generic_mail.html")
    body = template.render(
        {
            "image_url": "https://storage.googleapis.com/datak-production.appspot.com/ecommerce/prod/product_images/descuento.png",
            "body": get_body(email, code),
        }
    )
    
    send_email(subject, recipient_list, body)
