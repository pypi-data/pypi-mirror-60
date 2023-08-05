from .ema import EMA


class MACD:
    def __init__(self, slow_period: int, fast_period: int):
        self.slow = EMA(slow_period)
        self.fast = EMA(fast_period)
        self.avg_diff = EMA(slow_period)
        self.line = []

    def to_next(self, sdata, fdata):
        _fast = self.fast.to_next(fdata)
        _slow = self.slow.to_next(sdata)
        if _fast is None or _slow is None:
            self.line.append(None)
            return None
        diff = _fast-_slow
        self.line.append(diff)
        _avg = self.avg_diff.to_next(diff)
        if _avg is None:
            self.line.append(None)
            return None
        res = _avg - 2*diff
        self.line.append(res)
        return res


#
# class SMACDNormalized:
#     def __init__(self, slow_period: int, fast_period: int, range_period: int):
#         self.smacd = SMACD(slow_period, fast_period)
#         self.range = Range(period=range_period)
#         self.line = []
#
#     def to_next(self, data):
#         _range = self.range.to_next(data, data)
#         _smacd = self.smacd.to_next(data)
#         res = None
#         if not (_range is None or _smacd is None):
#             res = _range - _smacd
#         self.line.append(res)
#         return res

export = MACD
