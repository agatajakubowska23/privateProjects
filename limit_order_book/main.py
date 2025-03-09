from src.algorithms.limit_order_book import LimitOrderBook


orders = [
    ('SSBT', 'buy', 20, 80),
    ('SST', 'buy', 20, 30),
    ('SSTz', 'buy', 10, 30),
    ('SSTb', 'sell', 10, 10)
]

def run_limit_order_book(orders:list[tuple])->None:
    lob = LimitOrderBook()
    for order in orders:
        lob.add_order(*order)
    lob.cancel_order('SST')
    lob.cancel_order('AAA')

if __name__ == '__main__':
    run_limit_order_book(orders)