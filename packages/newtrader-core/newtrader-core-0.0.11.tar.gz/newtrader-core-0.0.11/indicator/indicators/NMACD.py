from .MACD import MACD
from .range import Range


class NMACD:
    def __init__(self, fast_p, slow_p):
        self.macd = MACD(fast_p, slow_p)
        self.range = Range(slow_p)
        self.line = []

    def to_next(self, price, high, low):
        macd = self.macd.to_next(price, price)
        r = self.range.to_next(high, low)
        if macd is not None and r is not None:
            self.line.append(macd / r)
            return self.line[-1]
        else:
            self.line.append(None)
            return None


export = NMACD
