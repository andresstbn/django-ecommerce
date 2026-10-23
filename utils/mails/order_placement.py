from django.template.loader import get_template
from .base import send_email

def get_body(customer):
    return f"""<strong>
            <span>Hola</span>, <span>{customer}</span> 
            <br>
            <span>
                Estamos felices de que te sumes a esta gran familia!
            </span>
            </strong>
            <h3>Hemos recibido tu pedido.</h3>
            <span>
                Vamos a preparar todo para que tus cuora lleguen a casa contigo. En breve recibiras un correo con los datos de envio
            </span>"""


def send_order_placement_mail(order):
    subject = "Cuora: Hemos recibido tu pedido!"
    recipient_list = [order.customer.email]
    
    template = get_template("ecommerce/generic_mail.html")
    body = template.render(
        {
            "order": order.id,
            "image_url": "https://storage.googleapis.com/datak-production.appspot.com/ecommerce/prod/product_images/pedido.jpg",
            "body": get_body(order.customer.name),
        }
    )
    bcc = order.commerce.notification_emails
    send_email(subject, recipient_list, body, bcc)
