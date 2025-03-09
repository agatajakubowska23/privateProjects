from sortedcontainers import SortedDict
from src.data_structures.order import Order
from collections import deque
import logging

logging.getLogger().setLevel(logging.INFO)


class LimitOrderBook:
    """
    LimitOrderBook is a class to organize buy and sell orders
    placed by traders.
    Main idea:
    - adding orders to two SortedDicts depending on the order side
    (buy -sorted descending or sell -sorted descending)
    - canceling orders if there is a need for that
    """
    def __init__(self):
        self.buy_orders = SortedDict(lambda x: -x)
        self.sell_orders = SortedDict()
        self.order_map = {}
        self.order_status = {}

    def add_order(
            self,
            order_id: str,
            side: str,
            price: int,
            quantity: int
    ) -> None:
        """
        To add new order to order and match limit prices with orders
        from opposite side
        Args:
            order_id: order id
            side: 'buy' or 'sell'
            price: the price of the order
            quantity: quantity of the order

        Returns:
            None

        """
        logging.info("Adding order")
        order = Order(order_id, side, price, quantity)
        self.order_status[order_id] = 'active'
        logging.info(f"{order} - OK")
        self.match_orders(order)
        if order.quantity > 0:
            order_book = self.buy_orders if side == 'buy' else self.sell_orders
            if price not in order_book:
                order_book[price] = deque()
            order_book[price].append(order)
            self.order_map[order_id] = order

    def cancel_order(self, order_id: str) -> bool:
        """
        Canceling order if there is a need for that
        Args:
            order_id: order id

        Returns:
            True if order was cancelled, False otherwise

        """
        logging.info('Cancelling order')
        if order_id not in self.order_map:
            if order_id not in self.order_status:
                logging.info(
                    f'Order {order_id} cancel failed - no such active order'
                )
                return False
            else:
                logging.info(
                    f'Order {order_id} cancel failed - already fully filled'
                )
                return False
        order = self.order_map.pop(order_id)
        order_book = (
            self.buy_orders) if order.side == 'buy' else self.sell_orders

        order_book[order.price].remove(order)
        if not order_book[order.price]:
            del order_book[order.price]
        self.order_status[order_id] = 'cancelled'
        logging.info(f'{order_id} Cancel, OK')
        return True

    def match_orders(self, order: Order) -> None:
        """
            Method that matches limit prices for orders from opposite side

            Args:
                order: instance of class Order

            Returns:
                None

            """
        matches = []

        if order.side == 'buy':
            book = self.sell_orders
            price_condition = lambda p: p <= order.price
        else:
            book = self.buy_orders
            price_condition = lambda p: p >= order.price

        while order.quantity > 0 and book:
            best_price = next(iter(book))

            if not price_condition(best_price):
                break

            resting_queue = book[best_price]

            while order.quantity > 0 and resting_queue:
                resting_order = resting_queue[0]
                executed_qty = min(order.quantity, resting_order.quantity)
                matches.append(
                    (
                        resting_order.order_id,
                        executed_qty,
                        best_price
                    )
                )

                order.quantity -= executed_qty
                resting_order.quantity -= executed_qty
                msg1 = (
                    f"""
{order} Fully matched with {
                    resting_order.order_id} ({executed_qty} @ {best_price})
"""
                )
                msg2 = (
                    f"""
{order} Partially matched with {
                    resting_order.order_id} ({executed_qty} @ {best_price})
                """
                )
                if order.quantity == 0:

                    logging.info(msg1)
                else:
                    logging.info(msg2)

                if resting_order.quantity == 0:
                    self.order_status[resting_order.order_id] = 'filled'
                    resting_queue.popleft()
                    if resting_order.order_id in self.order_map:
                        del self.order_map[resting_order.order_id]
                else:
                    self.order_status[resting_order.order_id] = 'partial'

            if not resting_queue:
                del book[best_price]

        if order.quantity == 0:
            self.order_status[order.order_id] = 'filled'
        elif matches:
            self.order_status[order.order_id] = 'partial'
        else:
            self.order_status[order.order_id] = 'active'
