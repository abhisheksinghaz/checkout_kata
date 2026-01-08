from dataclasses import dataclass, field
from typing import List, Dict
from collections import Counter

@dataclass
class CartItem:
    """Represents an item in the cart"""
    product_id: str
    quantity: int = 1

@dataclass
class Cart:
    """Cart model - manages items in shopping cart"""
    items: List[str] = field(default_factory=list)

    def add_item(self, product_id: str):
        """Add an item to cart"""
        self.items.append(product_id)

    def remove_item(self, product_id: str):
        """Remove one instance of an item"""
        if product_id in self.items:
            self.items.remove(product_id)

    def clear(self):
        """Empty the cart"""
        self.items.clear()

    def get_item_counts(self) -> Dict[str, int]:
        """Get count of each item type"""
        return dict(Counter(self.items))

    def get_total_items(self) -> int:
        """Get total number of items"""
        return len(self.items)