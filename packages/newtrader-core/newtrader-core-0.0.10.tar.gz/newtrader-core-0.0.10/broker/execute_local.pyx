from quotation.bar cimport Bar
from trade.trade cimport Direction, OrderType

cpdef float execute_market(Bar bar, Direction direction):
    if direction == Direction.BUY:
        return bar.ask_close
    else:
        return bar.bid_close

cpdef float execute_limit_order(Bar last_bar, Bar bar, Direction direction, float price):
    if direction == Direction.BUY:
        if bar.ask_high < price:
            return bar.ask_high
        if last_bar.ask_close > price >= bar.ask_low:
            return price
        else:
            return -1.0
    if direction == Direction.SELL:
        if bar.bid_low > price:
            return bar.bid_low
        elif last_bar.bid_close < price <= bar.bid_high:
            return price
        else:
            return -1.0

cpdef float execute_stop_order(Bar last_bar, Bar bar, Direction direction, float price):
    if direction == Direction.BUY:
        if bar.ask_low > price:
            return bar.ask_low
        elif last_bar.ask_close < price <= bar.ask_high:
            return price
        else:
            return -1.0
    if direction == Direction.SELL:
        if bar.bid_high < price:
            return bar.bid_high
        elif last_bar.bid_close > price >= bar.bid_low:
            return price
        else:
            return -1.0
cpdef float execute_limit_order_s(Bar bar, Direction direction, float price):
    if direction == Direction.BUY:
        if bar.ask_close <= price:
            return price
        else:
            return -1.0
    if direction == Direction.SELL:
        if bar.bid_close >= price:
            return price
        else:
            return -1.0
cpdef float execute_stop_order_s(Bar bar, Direction direction, float price):
    if direction == Direction.BUY:
        if bar.ask_close >= price:
            return price
        else:
            return -1.0
    if direction == Direction.SELL:
        if bar.bid_close <= price:
            return price
        else:
            return -1.0

cpdef tuple execute_els_order(Bar last_bar, Bar bar, Direction direction, float stop_price, float limit_price):
    cdef float price
    price = execute_limit_order(last_bar, bar, direction, limit_price)
    if price > 0:
        return price, OrderType.Limit
    price = execute_stop_order(last_bar, bar, direction, stop_price)
    if price > 0:
        return price, OrderType.Stop
    return -1.0,OrderType.INVALID
