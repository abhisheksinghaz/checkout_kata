from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    """Product model - represents a product entity"""
    product_id: str
    name: str
    unit_price: float
    active: bool = True

    def __post_init__(self):
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'unit_price': self.unit_price,
            'active': self.active
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)