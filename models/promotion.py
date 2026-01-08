from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict

class PromotionType(Enum):
    BULK_DISCOUNT = "bulk_discount"
    BUY_X_GET_Y_FREE = "buy_x_get_y_free"
    PERCENTAGE_OFF = "percentage_off"
    FIXED_DISCOUNT = "fixed_discount"
    TIERED_PRICING = "tiered_pricing"

@dataclass
class Promotion:
    """Promotion model - represents a promotional offer"""
    product_id: str
    promotion_type: PromotionType
    promotion_data: Dict
    start_date: datetime
    promotion_id: Optional[int] = None
    end_date: Optional[datetime] = None
    priority: int = 1
    active: bool = True

    def is_active(self, current_date: datetime = None) -> bool:
        """Check if promotion is currently active"""
        current_date = current_date or datetime.now()

        if not self.active:
            return False

        if self.start_date > current_date:
            return False

        if self.end_date and self.end_date < current_date:
            return False

        return True

    def to_dict(self):
        return {
            'promotion_id': self.promotion_id,
            'product_id': self.product_id,
            'promotion_type': self.promotion_type.value,
            'promotion_data': self.promotion_data,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'priority': self.priority,
            'active': self.active
        }