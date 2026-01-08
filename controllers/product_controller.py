from typing import Dict, List
from models.product import Product
from data.database import Database

class ProductController:
    """Controller for product operations"""

    def __init__(self, database: Database):
        self.db = database

    def create_product(self, product_id: str, name: str, unit_price: float) -> Dict:
        """Create a new product"""
        try:
            product = Product(
                product_id=product_id,
                name=name,
                unit_price=unit_price
            )
            self.db.add_product(product)

            return {
                'success': True,
                'message': f'Product {product_id} created successfully',
                'product': product.to_dict()
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }

    def get_product(self, product_id: str) -> Dict:
        """Get product details"""
        product = self.db.get_product(product_id)

        if not product:
            return {
                'success': False,
                'message': f'Product {product_id} not found'
            }

        return {
            'success': True,
            'product': product.to_dict()
        }

    def list_products(self) -> Dict:
        """List all products"""
        products = self.db.get_all_products()

        return {
            'success': True,
            'products': [p.to_dict() for p in products],
            'count': len(products)
        }

    def update_product(self, product_id: str, name: str = None,
                      unit_price: float = None) -> Dict:
        """Update product details"""
        product = self.db.get_product(product_id)

        if not product:
            return {
                'success': False,
                'message': f'Product {product_id} not found'
            }

        if name:
            product.name = name
        if unit_price is not None:
            product.unit_price = unit_price

        self.db.update_product(product)

        return {
            'success': True,
            'message': f'Product {product_id} updated successfully',
            'product': product.to_dict()
        }

    def delete_product(self, product_id: str) -> Dict:
        """Delete a product"""
        success = self.db.delete_product(product_id)

        if success:
            return {
                'success': True,
                'message': f'Product {product_id} deleted successfully'
            }
        else:
            return {
                'success': False,
                'message': f'Product {product_id} not found'
            }