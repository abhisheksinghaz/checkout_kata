from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Product(models.Model):
    """Product model"""
    product_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        ordering = ['product_id']

    def __str__(self):
        return f"{self.product_id} - {self.name}"


class Promotion(models.Model):
    """Promotion model"""

    PROMOTION_TYPES = [
        ('bulk_discount', 'Bulk Discount'),
        ('buy_x_get_y_free', 'Buy X Get Y Free'),
        ('percentage_off', 'Percentage Off'),
        ('fixed_discount', 'Fixed Discount'),
        ('tiered_pricing', 'Tiered Pricing'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    promotion_type = models.CharField(max_length=20, choices=PROMOTION_TYPES)
    promotion_data = models.JSONField()  # Stores flexible promotion parameters
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    priority = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'promotions'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['product', 'active', 'start_date', 'end_date']),
        ]

    def __str__(self):
        return f"Promotion {self.id} - {self.product.product_id} - {self.promotion_type}"

    def is_active_now(self):
        """Check if promotion is currently active"""
        now = timezone.now()

        if not self.active:
            return False

        if self.start_date > now:
            return False

        if self.end_date and self.end_date < now:
            return False

        return True


class Cart(models.Model):
    """Shopping cart model"""
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart {self.session_id}"

    def get_item_counts(self):
        """Get count of each product in cart"""
        from collections import Counter
        product_ids = list(self.items.values_list('product_id', flat=True))
        return dict(Counter(product_ids))

    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Items in a cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cart_items'

    def __str__(self):
        return f"{self.cart.session_id} - {self.product.product_id}"