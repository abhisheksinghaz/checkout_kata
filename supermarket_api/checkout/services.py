from decimal import Decimal
from typing import Optional, Dict, List
from django.utils import timezone
from django.db import models
from .models import Product, Promotion, Cart

class PricingEngine:
    """Business logic for calculating prices with promotions"""

    @staticmethod
    def calculate_price(product: Product, quantity: int,
                       promotion: Optional[Promotion] = None) -> Decimal:
        """Calculate price for given quantity with optional promotion"""
        unit_price = product.unit_price

        if not promotion or not promotion.is_active_now():
            return Decimal(quantity) * unit_price

        promo_type = promotion.promotion_type
        promo_data = promotion.promotion_data

        if promo_type == 'bulk_discount':
            return PricingEngine._calculate_bulk_discount(
                quantity, unit_price, promo_data
            )

        elif promo_type == 'buy_x_get_y_free':
            return PricingEngine._calculate_buy_x_get_y_free(
                quantity, unit_price, promo_data
            )

        elif promo_type == 'percentage_off':
            return PricingEngine._calculate_percentage_off(
                quantity, unit_price, promo_data
            )

        elif promo_type == 'fixed_discount':
            return PricingEngine._calculate_fixed_discount(
                quantity, unit_price, promo_data
            )

        elif promo_type == 'tiered_pricing':
            return PricingEngine._calculate_tiered_pricing(
                quantity, unit_price, promo_data
            )

        return Decimal(quantity) * unit_price

    @staticmethod
    def _calculate_bulk_discount(quantity: int, unit_price: Decimal,
                                 promo_data: Dict) -> Decimal:
        """Buy X for special price"""
        special_qty = promo_data['quantity']
        special_price = Decimal(str(promo_data['price']))

        special_sets = quantity // special_qty
        remaining = quantity % special_qty

        return (special_sets * special_price) + (remaining * unit_price)

    @staticmethod
    def _calculate_buy_x_get_y_free(quantity: int, unit_price: Decimal,
                                     promo_data: Dict) -> Decimal:
        """Buy X get Y free"""
        buy_qty = promo_data['buy_quantity']
        free_qty = promo_data['free_quantity']

        total_in_deal = buy_qty + free_qty
        full_deals = quantity // total_in_deal
        remaining = quantity % total_in_deal

        items_to_pay = (full_deals * buy_qty) + remaining
        return Decimal(items_to_pay) * unit_price

    @staticmethod
    def _calculate_percentage_off(quantity: int, unit_price: Decimal,
                                   promo_data: Dict) -> Decimal:
        """Percentage discount"""
        min_qty = promo_data.get('min_quantity', 1)
        discount_percent = Decimal(str(promo_data['discount_percent']))

        total = Decimal(quantity) * unit_price
        if quantity >= min_qty:
            total *= (Decimal('1') - discount_percent / Decimal('100'))
        return total

    @staticmethod
    def _calculate_fixed_discount(quantity: int, unit_price: Decimal,
                                   promo_data: Dict) -> Decimal:
        """Fixed amount discount per item"""
        min_qty = promo_data.get('min_quantity', 1)
        discount_amount = Decimal(str(promo_data['discount_amount']))

        if quantity >= min_qty:
            discounted_price = max(Decimal('0'), unit_price - discount_amount)
            return Decimal(quantity) * discounted_price
        return Decimal(quantity) * unit_price

    @staticmethod
    def _calculate_tiered_pricing(quantity: int, unit_price: Decimal,
                                   promo_data: Dict) -> Decimal:
        """Volume-based tiered pricing"""
        tiers = sorted(promo_data['tiers'], reverse=True)

        for min_qty, price_per_item in tiers:
            if quantity >= min_qty:
                return Decimal(quantity) * Decimal(str(price_per_item))

        return Decimal(quantity) * unit_price


class CheckoutService:
    """Service for checkout operations"""

    @staticmethod
    def get_or_create_cart(session_id: str) -> Cart:
        """Get or create cart for session"""
        cart, created = Cart.objects.get_or_create(session_id=session_id)
        return cart

    @staticmethod
    def calculate_cart_total(cart: Cart) -> Dict:
        """Calculate total for cart with promotions"""
        item_counts = cart.get_item_counts()

        total = Decimal('0')
        breakdown = []

        for product_id, quantity in item_counts.items():
            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                continue

            # Get highest priority active promotion
            promotions = Promotion.objects.filter(
                product=product,
                active=True,
                start_date__lte=timezone.now()
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=timezone.now())
            ).order_by('-priority', '-created_at')

            promotion = promotions.first() if promotions.exists() else None

            # Calculate price
            subtotal = PricingEngine.calculate_price(product, quantity, promotion)
            total += subtotal

            original_price = product.unit_price * quantity
            savings = original_price - subtotal

            breakdown.append({
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': float(product.unit_price),
                'promotion_type': promotion.promotion_type if promotion else None,
                'promotion_id': promotion.id if promotion else None,
                'subtotal': float(subtotal),
                'savings': float(savings)
            })

        total_savings = sum(item['savings'] for item in breakdown)

        return {
            'total': float(total),
            'item_count': sum(item_counts.values()),
            'breakdown': breakdown,
            'total_savings': float(total_savings)
        }