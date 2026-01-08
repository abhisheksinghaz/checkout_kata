import unittest
from datetime import datetime, timedelta
from data.database import Database
from controllers.checkout_controller import CheckoutController
from controllers.product_controller import ProductController
from controllers.promotion_controller import PromotionController
from models.promotion import PromotionType

class TestCheckoutController(unittest.TestCase):

    def setUp(self):
        """Setup test fixtures"""
        self.db = Database()
        self.product_ctrl = ProductController(self.db)
        self.promo_ctrl = PromotionController(self.db)
        self.checkout_ctrl = CheckoutController(self.db)

        # Add test products
        self.product_ctrl.create_product('A', 'Apple', 50)
        self.product_ctrl.create_product('B', 'Banana', 30)

        # Add test promotion
        self.promo_ctrl.create_promotion(
            'B',
            PromotionType.BULK_DISCOUNT.value,
            {'quantity': 2, 'price': 45}
        )

    def test_scan_item_success(self):
        """Test successful item scanning"""
        result = self.checkout_ctrl.scan_item('A')
        self.assertTrue(result['success'])
        self.assertEqual(result['cart_total_items'], 1)

    def test_scan_invalid_item(self):
        """Test scanning non-existent item"""
        result = self.checkout_ctrl.scan_item('Z')
        self.assertFalse(result['success'])

    def test_calculate_total_with_promotion(self):
        """Test total calculation with promotion"""
        # Scan B, A, B
        self.checkout_ctrl.scan_item('B')
        self.checkout_ctrl.scan_item('A')
        self.checkout_ctrl.scan_item('B')

        result = self.checkout_ctrl.calculate_total()

        # 2 B's (45) + 1 A (50) = 95
        self.assertEqual(result['total'], 95)
        self.assertEqual(result['item_count'], 3)

    def test_clear_cart(self):
        """Test cart clearing"""
        self.checkout_ctrl.scan_item('A')
        self.checkout_ctrl.clear_cart()

        summary = self.checkout_ctrl.get_cart_summary()
        self.assertEqual(summary['total_items'], 0)

if __name__ == '__main__':
    unittest.main()