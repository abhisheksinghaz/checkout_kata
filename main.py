from datetime import datetime, timedelta
from data.database import Database
from controllers.checkout_controller import CheckoutController
from controllers.product_controller import ProductController
from controllers.promotion_controller import PromotionController
from views.console_view import ConsoleView
from models.promotion import PromotionType

def setup_sample_data(db: Database, product_ctrl: ProductController,
                      promo_ctrl: PromotionController):
    """Setup sample products and promotions"""

    # Add products
    products = [
        ('A', 'Apple', 50),
        ('B', 'Banana', 30),
        ('C', 'Cherry', 20),
        ('D', 'Date', 15),
        ('E', 'Elderberry', 10),
    ]

    for product_id, name, price in products:
        product_ctrl.create_product(product_id, name, price)

    # Add promotions
    promo_ctrl.create_promotion(
        'A',
        PromotionType.BULK_DISCOUNT.value,
        {'quantity': 3, 'price': 130},
        end_date=datetime.now() + timedelta(days=30)
    )

    promo_ctrl.create_promotion(
        'B',
        PromotionType.BULK_DISCOUNT.value,
        {'quantity': 2, 'price': 45}
    )

    promo_ctrl.create_promotion(
        'C',
        PromotionType.BUY_X_GET_Y_FREE.value,
        {'buy_quantity': 2, 'free_quantity': 1}
    )

    promo_ctrl.create_promotion(
        'D',
        PromotionType.PERCENTAGE_OFF.value,
        {'min_quantity': 5, 'discount_percent': 20}
    )

    promo_ctrl.create_promotion(
        'E',
        PromotionType.TIERED_PRICING.value,
        {'tiers': [(1, 10), (5, 9), (10, 8)]}
    )

def main():
    """Application entry point"""

    # Initialize database
    db = Database()

    # Initialize controllers
    checkout_ctrl = CheckoutController(db)
    product_ctrl = ProductController(db)
    promo_ctrl = PromotionController(db)

    # Setup sample data
    setup_sample_data(db, product_ctrl, promo_ctrl)

    # Initialize view
    view = ConsoleView(checkout_ctrl, product_ctrl, promo_ctrl)

    # Run application
    view.run()

if __name__ == "__main__":
    main()