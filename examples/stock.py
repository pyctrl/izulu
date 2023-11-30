import logging
from dataclasses import dataclass

from izulu.root import Error

logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger(__name__)


class NotEnoughItem(Error):
    __features__ = 0
    __template__ = "Not enough {items} items"
    items: int


# Our domain model
@dataclass
class Stock:
    items: int

    def make_order(self, items: int) -> None:
        if items > self.items:
            # We already know how many items we need
            # So no need to request available items outside
            not_enough_items = items - self.items
            raise NotEnoughItem(items=not_enough_items)
        self.items -= items
        LOG.info("Ordered from the stock %d items", items)

    def make_order_from_warehouse(self, items: int) -> int:
        self.items += items
        LOG.info("Ordered from the warehouse %d items", items)


if __name__ == "__main__":
    # Initialize our stock
    stock = Stock(10)

    # Order 11 items
    items = 11
    try:
        stock.make_order(items)
    except NotEnoughItem as e:
        LOG.exception("NotEnoughItem exception:")

        # Not enough items in the our stock but we already
        # know how many items we need
        stock.make_order_from_warehouse(e.items)

        # Make the order again
        stock.make_order(items)
