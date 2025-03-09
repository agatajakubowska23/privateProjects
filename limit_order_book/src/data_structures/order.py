from dataclasses import dataclass


@dataclass
class Order:
    def __init__(self, order_id, side, price, quantity):
        self.order_id = order_id
        self.side = side.lower()
        self.price = price
        self.quantity = quantity
        self.original_quantity = quantity

    def __repr__(self):
        dsc = (
            f"""
{self.order_id} {self.side} {self.original_quantity} @ {self.price}
"""
        )
        return dsc
