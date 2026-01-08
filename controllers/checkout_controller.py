from typing import Dict, List, Tuple
from datetime import datetime
from models.cart import Cart
from models.product import Product
from models.promotion import Promotion
from data.database import Database
from services.pricing_engine import PricingEngine

class CheckoutController:
    """Controller for checkout operations"""

    def __init__(self, database: Database):
        self.db = database
        self.cart = Cart()

    def scan_item(self, product_id: str) -> Dict:
        """Scan an item and add to cart"""
        product = self.db.get_product(product_id)

        if not product:
            return {
                'success': False,
                'message': f'Product {product_id} not found'
            }

        if not product.active:
            return {
                'success': False,
                'message': f'Product {product_id} is not available'
            }

        self.cart.add_item(product_id)

        return {
            'success': True,
            'message': f'Added {product.name} to cart',
            'product': product.to_dict(),
            'cart_total_items': self.cart.get_total_items()
        }

    def remove_item(self, product_id: str) -> Dict:
        """Remove one instance of an item from cart"""
        self.cart.remove_item(product_id)
        return {
            'success': True,
            'message': f'Removed {product_id} from cart',
            'cart_total_items': self.cart.get_total_items()
        }

    def calculate_total(self, current_date: datetime = None) -> Dict:
        """Calculate total price with promotions"""
        current_date = current_date or datetime.now()
        item_counts = self.cart.get_item_counts()

        total = 0
        breakdown = []

        for product_id, quantity in item_counts.items():
            product = self.db.get_product(product_id)

            if not product:
                continue

            # Get active promotions for this product
            promotions = self.db.get_promotions_for_product(product_id, current_date)
            promotion = promotions[0] if promotions else None

            # Calculate price
            subtotal = PricingEngine.calculate_price(product, quantity, promotion)
            total += subtotal

            # Add to breakdown
            breakdown.append({
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': product.unit_price,
                'promotion_type': promotion.promotion_type.value if promotion else None,
                'promotion_id': promotion.promotion_id if promotion else None,
                'subtotal': round(subtotal, 2),
                'savings': round((quantity * product.unit_price) - subtotal, 2)
            })

        return {
            'total': round(total, 2),
            'item_count': self.cart.get_total_items(),
            'breakdown': breakdown,
            'total_savings': round(sum(item['savings'] for item in breakdown), 2)
        }

    def clear_cart(self) -> Dict:
        """Clear all items from cart"""
        self.cart.clear()
        return {
            'success': True,
            'message': 'Cart cleared'
        }

    def get_cart_summary(self) -> Dict:
        """Get current cart summary"""
        item_counts = self.cart.get_item_counts()
        items = []

        for product_id, quantity in item_counts.items():
            product = self.db.get_product(product_id)
            if product:
                items.append({
                    'product_id': product_id,
                    'name': product.name,
                    'quantity': quantity,
                    'unit_price': product.unit_price
                })

        return {
            'items': items,
            'total_items': self.cart.get_total_items()
        }