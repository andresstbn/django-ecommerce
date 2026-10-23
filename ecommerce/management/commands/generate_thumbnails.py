from django.core.management.base import BaseCommand
from ecommerce.models import ProductImage


class Command(BaseCommand):
    help = "Generates WebP thumbnail/medium variants for product images. Safe to re-run: originals are never modified and up-to-date images are skipped."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Only list the images that would be processed.")
        parser.add_argument("--force", action="store_true", help="Regenerate even if variants already exist.")
        parser.add_argument("--commerce", type=int, help="Limit to one commerce id.")

    def handle(self, *args, dry_run=False, force=False, commerce=None, **options):
        images = ProductImage.objects.exclude(image="").order_by("id")
        if commerce:
            images = images.filter(product__commerce_id=commerce)

        done = skipped = failed = 0
        for product_image in images.iterator():
            if product_image.has_variants() and not force:
                skipped += 1
                continue
            if dry_run:
                self.stdout.write(f"would process {product_image.pk} {product_image.image.name}")
                done += 1
                continue
            try:
                product_image.generate_variants()
                done += 1
                self.stdout.write(f"ok {product_image.pk} -> {product_image.thumbnail.name}")
            except Exception as e:
                failed += 1
                self.stderr.write(f"failed {product_image.pk} {product_image.image.name}: {e}")

        self.stdout.write(f"processed={done} skipped={skipped} failed={failed}")
