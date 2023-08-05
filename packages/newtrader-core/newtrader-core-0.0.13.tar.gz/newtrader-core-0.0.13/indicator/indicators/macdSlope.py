from indicator.indicators import MACD, SimpleSlope


class MACDSlope:
    def __init__(self, slow_period, fast_period, slope_period):
        self.macd = MACD.MACD(slow_period, fast_period)
        self.slope = SimpleSlope.SimpleSlope(slope_period)
        self.line = []

    def to_next(self, slow_data, fast_data):
        macd = self.macd.to_next(slow_data, fast_data)
        if macd is None:
            self.line.append(None)
            return None
        slope = self.slope.to_next(macd)
        if slope is None:
            self.line.append(None)
            return None
        self.line.append(slope)
        return slope



export = MACDSlope