from typing import List, Optional, Dict
from datetime import datetime
from models.product import Product
from models.promotion import Promotion, PromotionType

class Database:
    """In-memory database simulation - can be replaced with SQLAlchemy/SQL"""

    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.promotions: List[Promotion] = []
        self.promotion_id_counter = 1

    # Product operations
    def add_product(self, product: Product) -> Product:
        """Add a product to database"""
        if product.product_id in self.products:
            raise ValueError(f"Product {product.product_id} already exists")
        self.products[product.product_id] = product
        return product

    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)

    def get_all_products(self) -> List[Product]:
        """Get all products"""
        return list(self.products.values())

    def update_product(self, product: Product) -> Product:
        """Update existing product"""
        if product.product_id not in self.products:
            raise ValueError(f"Product {product.product_id} not found")
        self.products[product.product_id] = product
        return product

    def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False

    # Promotion operations
    def add_promotion(self, promotion: Promotion) -> Promotion:
        """Add a promotion to database"""
        promotion.promotion_id = self.promotion_id_counter
        self.promotion_id_counter += 1
        self.promotions.append(promotion)
        return promotion

    def get_promotion(self, promotion_id: int) -> Optional[Promotion]:
        """Get promotion by ID"""
        for promo in self.promotions:
            if promo.promotion_id == promotion_id:
                return promo
        return None

    def get_promotions_for_product(self, product_id: str,
                                   current_date: datetime = None) -> List[Promotion]:
        """Get all active promotions for a product"""
        current_date = current_date or datetime.now()

        active_promos = [
            p for p in self.promotions
            if p.product_id == product_id and p.is_active(current_date)
        ]

        # Sort by priority (highest first)
        return sorted(active_promos, key=lambda x: x.priority, reverse=True)

    def update_promotion(self, promotion: Promotion) -> Promotion:
        """Update existing promotion"""
        for i, promo in enumerate(self.promotions):
            if promo.promotion_id == promotion.promotion_id:
                self.promotions[i] = promotion
                return promotion
        raise ValueError(f"Promotion {promotion.promotion_id} not found")

    def deactivate_promotion(self, promotion_id: int) -> bool:
        """Deactivate a promotion"""
        for promo in self.promotions:
            if promo.promotion_id == promotion_id:
                promo.active = False
                return True
        return False