from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from checkout.models import Product, Promotion

class Command(BaseCommand):
    help = 'Load sample products and promotions'

    def handle(self, *args, **kwargs):
        # Create products
        products_data = [
            ('A', 'Apple', 50),
            ('B', 'Banana', 30),
            ('C', 'Cherry', 20),
            ('D', 'Date', 15),
            ('E', 'Elderberry', 10),
        ]

        for product_id, name, price in products_data:
            product, created = Product.objects.get_or_create(
                product_id=product_id,
                defaults={'name': name, 'unit_price': price}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created product: {product_id}'))

        # Create promotions
        promotions_data = [
            ('A', 'bulk_discount', {'quantity': 3, 'price': 130}),
            ('B', 'bulk_discount', {'quantity': 2, 'price': 45}),
            ('C', 'buy_x_get_y_free', {'buy_quantity': 2, 'free_quantity': 1}),
            ('D', 'percentage_off', {'min_quantity': 5, 'discount_percent': 20}),
            ('E', 'tiered_pricing', {'tiers': [[1, 10], [5, 9], [10, 8]]}),
        ]

        for product_id, promo_type, promo_data in promotions_data:
            product = Product.objects.get(product_id=product_id)
            promotion, created = Promotion.objects.get_or_create(
                product=product,
                promotion_type=promo_type,
                defaults={
                    'promotion_data': promo_data,
                    'start_date': timezone.now(),
                    'end_date': timezone.now() + timedelta(days=30)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created promotion for {product_id}: {promo_type}'
                ))

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))