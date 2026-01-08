from typing import Optional, Dict
from models.product import Product
from models.promotion import Promotion, PromotionType

class PricingEngine:
    """Business logic for calculating prices with promotions"""

    @staticmethod
    def calculate_price(product: Product, quantity: int,
                       promotion: Optional[Promotion] = None) -> float:
        """Calculate price for given quantity with optional promotion"""
        unit_price = product.unit_price

        if not promotion:
            return quantity * unit_price

        promo_type = promotion.promotion_type
        promo_data = promotion.promotion_data

        if promo_type == PromotionType.BULK_DISCOUNT:
            return PricingEngine._calculate_bulk_discount(
                quantity, unit_price, promo_data
            )

        elif promo_type == PromotionType.BUY_X_GET_Y_FREE:
            return PricingEngine._calculate_buy_x_get_y_free(
                quantity, unit_price, promo_data
            )

        elif promo_type == PromotionType.PERCENTAGE_OFF:
            return PricingEngine._calculate_percentage_off(
                quantity, unit_price, promo_data
            )

        elif promo_type == PromotionType.FIXED_DISCOUNT:
            return PricingEngine._calculate_fixed_discount(
                quantity, unit_price, promo_data
            )

        elif promo_type == PromotionType.TIERED_PRICING:
            return PricingEngine._calculate_tiered_pricing(
                quantity, unit_price, promo_data
            )

        return quantity * unit_price

    @staticmethod
    def _calculate_bulk_discount(quantity: int, unit_price: float,
                                 promo_data: Dict) -> float:
        """Buy X for special price"""
        special_qty = promo_data['quantity']
        special_price = promo_data['price']

        special_sets = quantity // special_qty
        remaining = quantity % special_qty

        return (special_sets * special_price) + (remaining * unit_price)

    @staticmethod
    def _calculate_buy_x_get_y_free(quantity: int, unit_price: float,
                                     promo_data: Dict) -> float:
        """Buy X get Y free"""
        buy_qty = promo_data['buy_quantity']
        free_qty = promo_data['free_quantity']

        total_in_deal = buy_qty + free_qty
        full_deals = quantity // total_in_deal
        remaining = quantity % total_in_deal

        items_to_pay = (full_deals * buy_qty) + remaining
        return items_to_pay * unit_price

    @staticmethod
    def _calculate_percentage_off(quantity: int, unit_price: float,
                                   promo_data: Dict) -> float:
        """Percentage discount"""
        min_qty = promo_data.get('min_quantity', 1)
        discount_percent = promo_data['discount_percent']

        total = quantity * unit_price
        if quantity >= min_qty:
            total *= (1 - discount_percent / 100)
        return total

    @staticmethod
    def _calculate_fixed_discount(quantity: int, unit_price: float,
                                   promo_data: Dict) -> float:
        """Fixed amount discount per item"""
        min_qty = promo_data.get('min_quantity', 1)
        discount_amount = promo_data['discount_amount']

        if quantity >= min_qty:
            discounted_price = max(0, unit_price - discount_amount)
            return quantity * discounted_price
        return quantity * unit_price

    @staticmethod
    def _calculate_tiered_pricing(quantity: int, unit_price: float,
                                   promo_data: Dict) -> float:
        """Volume-based tiered pricing"""
        tiers = sorted(promo_data['tiers'], reverse=True)

        for min_qty, price_per_item in tiers:
            if quantity >= min_qty:
                return quantity * price_per_item

        return quantity * unit_price