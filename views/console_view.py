from typing import Dict
from controllers.checkout_controller import CheckoutController
from controllers.product_controller import ProductController
from controllers.promotion_controller import PromotionController

class ConsoleView:
    """Console-based user interface"""

    def __init__(self, checkout_controller: CheckoutController,
                 product_controller: ProductController,
                 promotion_controller: PromotionController):
        self.checkout_ctrl = checkout_controller
        self.product_ctrl = product_controller
        self.promotion_ctrl = promotion_controller

    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*50)
        print("  SUPERMARKET CHECKOUT SYSTEM")
        print("="*50 + "\n")

    def display_menu(self):
        """Display main menu"""
        print("\n--- MAIN MENU ---")
        print("1. Scan Item")
        print("2. View Cart")
        print("3. Calculate Total")
        print("4. Clear Cart")
        print("5. View Products")
        print("6. View Promotions")
        print("7. Exit")
        print("-" * 20)

    def display_products(self):
        """Display all products"""
        result = self.product_ctrl.list_products()

        if not result['success'] or not result['products']:
            print("\nNo products available.")
            return

        print("\n--- AVAILABLE PRODUCTS ---")
        print(f"{'ID':<5} {'Name':<20} {'Price':<10} {'Status'}")
        print("-" * 50)

        for product in result['products']:
            status = "Active" if product['active'] else "Inactive"
            print(f"{product['product_id']:<5} {product['name']:<20} "
                  f"Rs {product['unit_price']:<8.2f} {status}")

    def display_cart(self):
        """Display cart contents"""
        cart = self.checkout_ctrl.get_cart_summary()

        if not cart['items']:
            print("\nYour cart is empty.")
            return

        print("\n--- YOUR CART ---")
        print(f"{'ID':<5} {'Name':<20} {'Qty':<5} {'Unit Price'}")
        print("-" * 50)

        for item in cart['items']:
            print(f"{item['product_id']:<5} {item['name']:<20} "
                  f"{item['quantity']:<5} Rs {item['unit_price']:.2f}")

        print(f"\nTotal Items: {cart['total_items']}")

    def display_total(self):
        """Display checkout total with breakdown"""
        result = self.checkout_ctrl.calculate_total()

        if not result['breakdown']:
            print("\nYour cart is empty.")
            return

        print("\n" + "="*70)
        print("  CHECKOUT SUMMARY")
        print("="*70)

        print(f"\n{'Product':<20} {'Qty':<5} {'Unit':<8} {'Promo':<15} {'Subtotal':<10} {'Saved'}")
        print("-" * 70)

        for item in result['breakdown']:
            promo = item['promotion_type'] or 'None'
            print(f"{item['product_name']:<20} {item['quantity']:<5} "
                  f"Rs {item['unit_price']:<6.2f} {promo:<15} "
                  f"Rs {item['subtotal']:<8.2f} Rs {item['savings']:.2f}")

        print("-" * 70)
        print(f"{'TOTAL SAVINGS:':<55} Rs {result['total_savings']:.2f}")
        print(f"{'TOTAL TO PAY:':<55} Rs {result['total']:.2f}")
        print("="*70 + "\n")

    def scan_item_flow(self):
        """Handle item scanning"""
        self.display_products()
        product_id = input("\nEnter Product ID to scan (or 'back'): ").strip().upper()

        if product_id == 'BACK':
            return

        result = self.checkout_ctrl.scan_item(product_id)

        if result['success']:
            print(f"✓ {result['message']}")
            print(f"  Cart now has {result['cart_total_items']} items")
        else:
            print(f"✗ {result['message']}")

    def view_promotions_flow(self):
        """View promotions for a product"""
        product_id = input("\nEnter Product ID to view promotions (or 'back'): ").strip().upper()

        if product_id == 'BACK':
            return

        result = self.promotion_ctrl.list_promotions_for_product(product_id)

        if not result['success'] or not result['promotions']:
            print(f"\nNo active promotions for product {product_id}.")
            return

        print(f"\n--- PROMOTIONS FOR {product_id} ---")
        for promo in result['promotions']:
            print(f"\nPromotion ID: {promo['promotion_id']}")
            print(f"Type: {promo['promotion_type']}")
            print(f"Details: {promo['promotion_data']}")
            print(f"Valid: {promo['start_date']} to {promo['end_date'] or 'Ongoing'}")

    def run(self):
        """Main application loop"""
        self.display_welcome()

        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == '1':
                self.scan_item_flow()
            elif choice == '2':
                self.display_cart()
            elif choice == '3':
                self.display_total()
            elif choice == '4':
                self.checkout_ctrl.clear_cart()
                print("\n✓ Cart cleared!")
            elif choice == '5':
                self.display_products()
            elif choice == '6':
                self.view_promotions_flow()
            elif choice == '7':
                print("\nThank you for shopping with us!")
                break
            else:
                print("\n✗ Invalid choice. Please try again.")

            input("\nPress Enter to continue...")