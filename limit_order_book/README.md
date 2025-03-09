### Limit Order Book

The Limit Order Book is a Python module for managing and matching buy and sell orders. It uses SortedDict from the sortedcontainers package to maintain separate order books for each side. Orders are added, automatically matched against opposing orders, or cancelled as needed. Logging is used at the INFO level to track order activity.

#### Available commands

1. Create an Instance of LimitOrderBook

Before adding or canceling orders, you need to create an instance of the LimitOrderBook:

```
from src.data_structures.limit_order_book import LimitOrderBook

lob = LimitOrderBook()
```

2. Add Multiple Orders on the Same Instance

You can use the same lob instance to add multiple orders:

```
lob.add_order(order_id='order1', side='buy', price=100, quantity=10)
lob.add_order(order_id='order2', side='sell', price=105, quantity=5)
print('Orders added')

```
3. Cancel an Order on the Same Instance

Once the order is added, you can cancel it using the same instance:


```
result = lob.cancel_order('order1')
```

Since order matching is performed automatically during order addition, you can simulate matching by adding complementary orders:

4. Simulate Order Matching

Since order matching is performed automatically during order addition, you can simulate matching by adding complementary orders:

```
lob.add_order(order_id='order3', side='buy', price=105, quantity=5)  # Matches with order2
lob.add_order(order_id='order4', side='sell', price=100, quantity=10)  # Matches with order1
```

###  Description
The Limit Order Book module organizes buy and sell orders from traders. It maintains:

Buy Orders: Stored in a SortedDict sorted in descending order (highest bid first).
Sell Orders: Stored in a SortedDict sorted in ascending order (lowest ask first).
Orders are stored in deques at each price level for efficient processing. The module includes functions to add orders, cancel orders, and match orders based on price conditions.

### Dependencies
Python 3.x

Install required dependencies:



```bash
pip install -r requirements.txt
```

Custom Order class: Located at src/data_structures/order.py

Standard Libraries: collections, logging



### Logging
The module sets the logging level to INFO to provide feedback on operations such as adding, cancelling, and matching orders. Adjust logging configurations as needed for your project.

