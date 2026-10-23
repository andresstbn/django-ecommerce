import tempfile
from decimal import Decimal
from io import BytesIO, StringIO

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from ecommerce.models import (
    AttributeOption,
    AttributeValue,
    Commerce,
    Order,
    Product,
    ProductAttribute,
    ProductImage,
)
from users.models import BaseUser

TEST_SETTINGS = dict(
    STORAGES={
        # Overwrites like GS_FILE_OVERWRITE in production.
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": tempfile.mkdtemp(), "allow_overwrite": True},
        },
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)


def jpeg(size=(3000, 2000), orientation=None):
    buffer = BytesIO()
    img = Image.new("RGB", size, "red")
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation
    img.save(buffer, format="JPEG", exif=exif)
    return SimpleUploadedFile("DSC0001.JPG", buffer.getvalue(), content_type="image/jpeg")


@override_settings(**TEST_SETTINGS)
class StoreTestCase(TestCase):
    def setUp(self):
        self.commerce = Commerce.objects.create(name="Cuora", notification_emails=["ventas@example.com"])
        self.user = BaseUser.objects.create_user(email="api@example.com", password="x")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {Token.objects.create(user=self.user).key}")

    def make_product(self, name="Zapato", price=100000, **kwargs):
        product = Product.objects.create(commerce=self.commerce, name=name, price=price, published=True, **kwargs)
        size = ProductAttribute.objects.create(name="Talla", commerce=self.commerce)
        color = ProductAttribute.objects.create(name="Color", commerce=self.commerce)
        s25, s26 = (AttributeOption.objects.create(attribute=size, name=n) for n in ("25", "26"))
        red = AttributeOption.objects.create(attribute=color, name="Rojo")
        for option, stock in ((s25, 3), (s26, 0)):
            value = AttributeValue.objects.create(product=product, stock=stock)
            value.attribute_options.set([option, red])
        return product


class ProductImageVariantsTest(StoreTestCase):
    def test_upload_generates_webp_variants_and_keeps_original(self):
        product = self.make_product()
        image = ProductImage.objects.create(product=product, image=jpeg())

        self.assertTrue(image.has_variants())
        self.assertTrue(image.thumbnail.name.endswith("_thumb.webp"))
        thumb = Image.open(image.thumbnail)
        self.assertEqual((thumb.format, max(thumb.size)), ("WEBP", 600))
        medium = Image.open(image.image.storage.open(image.thumbnail.name.replace("_thumb", "_medium")))
        self.assertEqual(max(medium.size), 1600)
        self.assertEqual(Image.open(image.image.storage.open(image.image.name)).size, (3000, 2000))  # original untouched
        self.assertTrue(image.medium_url().endswith("_medium.webp"))

    def test_respects_exif_orientation(self):
        image = ProductImage.objects.create(product=self.make_product(), image=jpeg(orientation=6))
        self.assertEqual(Image.open(image.thumbnail).size, (400, 600))  # rotated to portrait

    def test_broken_image_does_not_block_upload(self):
        bad = SimpleUploadedFile("x.jpg", b"not an image")
        with self.assertLogs("ecommerce.models.product_image", "ERROR"):
            image = ProductImage.objects.create(product=self.make_product(), image=bad)
        self.assertFalse(image.has_variants())
        self.assertEqual(image.medium_url(), image.image.url)

    def test_regeneration_command_is_idempotent(self):
        product = self.make_product()
        legacy = ProductImage.objects.create(product=product, image=jpeg())
        # Simulate a legacy row (manual/PNG thumbnail) without touching save().
        ProductImage.objects.filter(pk=legacy.pk).update(thumbnail="ecommerce/dev/product_images/DSC_thumbnail.JPG")

        out = StringIO()
        call_command("generate_thumbnails", "--dry-run", stdout=out)
        self.assertIn("processed=1 skipped=0", out.getvalue())
        legacy.refresh_from_db()
        self.assertFalse(legacy.has_variants())

        call_command("generate_thumbnails", stdout=out)
        legacy.refresh_from_db()
        self.assertTrue(legacy.has_variants())

        out = StringIO()
        call_command("generate_thumbnails", stdout=out)
        self.assertIn("processed=0 skipped=1 failed=0", out.getvalue())


class CatalogTest(StoreTestCase):
    def test_public_products_payload(self):
        product = self.make_product()
        ProductImage.objects.create(product=product, image=jpeg())

        res = self.client.get("/v1/commercePublic/products/", {"commerce": self.commerce.id})

        self.assertEqual(res.status_code, 200)
        item = res.json()["results"][0]
        self.assertEqual(item["attribute_values"], {"Color": {"Rojo": 0}, "Talla": {"26": 0, "25": 3}})
        self.assertEqual(list(item["attribute_values"]), ["Color", "Talla"])  # key order preserved
        self.assertEqual(set(item["images"][0]), {"id", "image", "thumbnail", "medium"})
        self.assertEqual(Decimal(item["price_with_discount"]), Decimal("100000"))

    def test_query_count_does_not_grow_with_products(self):
        def count():
            with CaptureQueriesContext(connection) as ctx:
                self.client.get("/v1/commercePublic/products/", {"commerce": self.commerce.id, "page_size": 100})
            return len(ctx)

        self.make_product("A")
        baseline = count()
        for name in "BCDEFG":
            ProductImage.objects.create(product=self.make_product(name), image=jpeg((60, 40)))
        self.assertEqual(count(), baseline)


class CheckoutTest(StoreTestCase):
    def test_order_placement_amounts_and_items(self):
        product = self.make_product(price=100000, discount_percentage=10)
        payload = {
            "municipality": "Cúcuta", "department": "Norte de Santander", "address": "Calle 1",
            "phone": "3000000000", "email": "cliente@example.com", "name": "Ana", "last_name": "Pérez",
            "document_number": "123", "commerce": self.commerce.id,
            "products": [{"id": product.id, "qty": 2, "size": "25"}],
        }

        res = self.client.post("/v1/commercePublic/orderPlacement/", payload, format="json")

        self.assertEqual(res.status_code, 200, res.content)
        order = Order.objects.get(pk=res.json()["id"])
        self.assertEqual(order.items.get().quantity, 2)
        self.assertEqual(order.subtotal_amount, Decimal("200000"))
        self.assertEqual(order.discount_amount, Decimal("10000"))  # per-item discount, as in production
        self.assertEqual(order.amount, Decimal("206500"))  # + 16.500 shipping


class EmailTest(StoreTestCase):
    def test_subscription_sends_coupon_email(self):
        res = self.client.post("/v1/emailSubscriptions/subscribe/", {"email": "nuevo@example.com", "commerce": self.commerce.id}, format="json")

        self.assertTrue(res.json()["success"])
        self.assertEqual(mail.outbox[0].to, ["nuevo@example.com"])
        self.assertEqual(mail.outbox[0].content_subtype, "html")

    def test_send_email_requires_authentication(self):
        body = {"subject": "Hola", "recipient_list": ["x@example.com"], "body": "<b>hi</b>"}
        self.assertIn(APIClient().post("/v1/commercePublic/sendEmail", body, format="json").status_code, (401, 403))
        self.assertEqual(self.client.post("/v1/commercePublic/sendEmail", body, format="json").status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
