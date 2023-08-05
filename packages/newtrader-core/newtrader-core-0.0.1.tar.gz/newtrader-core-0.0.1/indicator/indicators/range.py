from .high import High
from .low import Low


class Range:
    def __init__(self, period: int):
        self.period = period
        self.line = []
        self.high = High(period)
        self.low = Low(period)

    def to_next(self, high, low):
        _high = self.high.to_next(high)
        _low = self.low.to_next(low)
        _range = None
        if _high is not None and _low is not None:
            _range = _high - _low
        self.line.append(_range)
        return _range


export = Range
