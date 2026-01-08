from typing import Dict, List
from datetime import datetime
from models.promotion import Promotion, PromotionType
from data.database import Database

class PromotionController:
    """Controller for promotion operations"""

    def __init__(self, database: Database):
        self.db = database

    def create_promotion(self, product_id: str, promotion_type: str,
                        promotion_data: Dict, start_date: datetime = None,
                        end_date: datetime = None, priority: int = 1) -> Dict:
        """Create a new promotion"""
        try:
            # Validate product exists
            product = self.db.get_product(product_id)
            if not product:
                return {
                    'success': False,
                    'message': f'Product {product_id} not found'
                }

            # Parse promotion type
            promo_type = PromotionType(promotion_type)

            promotion = Promotion(
                product_id=product_id,
                promotion_type=promo_type,
                promotion_data=promotion_data,
                start_date=start_date or datetime.now(),
                end_date=end_date,
                priority=priority
            )

            self.db.add_promotion(promotion)

            return {
                'success': True,
                'message': f'Promotion created for product {product_id}',
                'promotion': promotion.to_dict()
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }

    def get_promotion(self, promotion_id: int) -> Dict:
        """Get promotion details"""
        promotion = self.db.get_promotion(promotion_id)

        if not promotion:
            return {
                'success': False,
                'message': f'Promotion {promotion_id} not found'
            }

        return {
            'success': True,
            'promotion': promotion.to_dict()
        }

    def list_promotions_for_product(self, product_id: str) -> Dict:
        """List all active promotions for a product"""
        promotions = self.db.get_promotions_for_product(product_id)

        return {
            'success': True,
            'product_id': product_id,
            'promotions': [p.to_dict() for p in promotions],
            'count': len(promotions)
        }

    def deactivate_promotion(self, promotion_id: int) -> Dict:
        """Deactivate a promotion"""
        success = self.db.deactivate_promotion(promotion_id)

        if success:
            return {
                'success': True,
                'message': f'Promotion {promotion_id} deactivated'
            }
        else:
            return {
                'success': False,
                'message': f'Promotion {promotion_id} not found'
            }