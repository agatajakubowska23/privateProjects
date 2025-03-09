### Limit Order Book

The Limit Order Book is a Python module for managing and matching buy and sell orders. It uses SortedDict from the sortedcontainers package to maintain separate order books for each side. Orders are added, automatically matched against opposing orders, or cancelled as needed. Logging is used at the INFO level to track order activity.

#### Available commands

##### To add a new order

```bash
python3 -c "from src.data_structures.limit_order_book import LimitOrderBook; \
lob = LimitOrderBook(); \
lob.add_order(order_id='order1', side='buy', price=100, quantity=10); \
print('Order added')"

```
##### To cancel an order
```bash

python3 -c "from src.data_structures.limit_order_book import LimitOrderBook; \
lob = LimitOrderBook(); \
lob.add_order(order_id='order1', side='buy', price=100, quantity=10); \
result = lob.cancel_order('order1'); \
print('Cancel order result:', result)"
```

Since order matching is performed automatically during order addition, you can simulate matching by adding complementary orders:

###### To test order matching
```bash

Since order matching is performed automatically during order addition, you can simulate matching by adding complementary orders:

```

###  Description
The Limit Order Book module organizes buy and sell orders from traders. It maintains:

Buy Orders: Stored in a SortedDict sorted in descending order (highest bid first).
Sell Orders: Stored in a SortedDict sorted in ascending order (lowest ask first).
Orders are stored in deques at each price level for efficient processing. The module includes functions to add orders, cancel orders, and match orders based on price conditions.

Dependencies
Python 3.x
sortedcontainers: Install using:
bash
Copy
Edit



```bash

pip install sortedcontainers
```

Custom Order class: Located at src/data_structures/order.py
Standard Libraries: collections, logging

### Logging
The module sets the logging level to INFO to provide feedback on operations such as adding, cancelling, and matching orders. Adjust logging configurations as needed for your project.

Setup
Ensure your PYTHONPATH includes your project directory. For example:

```bash

export PYTHONPATH='<your path>/data01'

```

export PYTHONPATH='<your path>/data01'
