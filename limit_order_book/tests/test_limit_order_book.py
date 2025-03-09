import pytest
from unittest.mock import MagicMock
from src.algorithms import limit_order_book
from src.data_structures.order import Order
from sortedcontainers import SortedDict
import logging


@pytest.fixture
def limit_order_book_object():
    return limit_order_book.LimitOrderBook()

@pytest.fixture
def limit_order_book_full_object(limit_order_book_object):
    limit_order_book_object.add_order("AAA", "buy", 20, 10)
    limit_order_book_object.add_order("ABA", "buy", 10, 10)
    limit_order_book_object.add_order("AAB", "buy", 20, 10)
    return limit_order_book_object
    # orders = [("AAA", "buy", 20, 10), ("ABA", "buy", 10, 10), ("AAB", "buy", 20, 10)]
    # for order in orders:
    #     limit_order_book_object.add_order(*order)
    # return limit_order_book_object

def test_limit_order_initialization(limit_order_book_object):
    assert isinstance(limit_order_book_object.buy_orders, SortedDict)
    assert isinstance(limit_order_book_object.sell_orders, SortedDict)
    assert limit_order_book_object.order_map =={}
    assert limit_order_book_object.order_status == {}


def test_add_order(limit_order_book_full_object, caplog):
    limit_order_book_full_object.match_orders=MagicMock()
    with caplog.at_level(logging.INFO):
        assert len(limit_order_book_full_object.order_map) == 3
        limit_order_book_full_object.add_order("AAA", "buy", 70, 10)
        assert 'AAA buy 10 @ 70 - OK\n' in caplog.text
        args = limit_order_book_full_object.match_orders.call_args
        assert len(args) == 2
        assert isinstance(args[0][0], Order)


@pytest.mark.parametrize("test_order_id,expected_log", [
    ('ABC','Order ABC cancel failed - no such active order\n'),
    ('SSTz','Order SSTz cancel failed - already fully filled\n')
])
def test_cancel_order(limit_order_book_object, caplog, test_order_id,expected_log):
    limit_order_book_object.order_map = {
        'SSBT': Order('SSBT', 'buy', 2,5),
        'SST': Order('SST', 'buy', 1,10)}
    limit_order_book_object.order_status = {'SSBT': 'active', 'SST': 'active', 'SSTz': 'filled'}
    with caplog.at_level(logging.INFO):
        limit_order_book_object.cancel_order(test_order_id)
        assert len(limit_order_book_object.order_map) == 2
        assert expected_log in caplog.text

@pytest.mark.parametrize("test_order,res1, res2,res3,expected_log1,expected_log2", [
    (('SST', 'sell', 10 ,5),3, ['AAA', 'ABA', 'AAB'],{'AAA': 'partial', 'AAB': 'active', 'ABA': 'active', 'SST': 'filled'},'SST sell 5 @ 10 - OK\n', 'SST sell 5 @ 10 Fully matched with AAA (5 @ 20)\n'),
(("SST", "sell", 20, 30), 2,['ABA', 'SST'],{'AAA': 'filled', 'AAB': 'filled', 'ABA': 'active', 'SST': 'partial'},'SST sell 30 @ 20 - OK\n', 'SST sell 30 @ 20 Partially matched with AAB (10 @ 20)\n')
])
def test_match_orders(limit_order_book_full_object, caplog, test_order,res1,res2,res3,expected_log1,expected_log2):
    with caplog.at_level(logging.INFO):
        assert len(limit_order_book_full_object.order_map) == 3
        assert limit_order_book_full_object.order_status=={'AAA': 'active', 'AAB': 'active', 'ABA': 'active'}
        limit_order_book_full_object.add_order(*test_order)
        assert len(limit_order_book_full_object.order_map) == res1
        assert list(limit_order_book_full_object.order_map.keys()) == res2
        assert limit_order_book_full_object.order_status==res3
        assert expected_log1 in caplog.text
        assert expected_log2 in caplog.text



