import pytest
from src.data_structures import order

def test_order_initialization():
    new_order = order.Order('ABC', "buy", 3, 4)
    assert new_order is not None
    assert new_order.__dict__==  {'order_id': 'ABC', 'side': 'buy', 'price': 3, 'quantity': 4, 'original_quantity': 4}
    assert   repr(new_order) == 'ABC buy 4 @ 3'




