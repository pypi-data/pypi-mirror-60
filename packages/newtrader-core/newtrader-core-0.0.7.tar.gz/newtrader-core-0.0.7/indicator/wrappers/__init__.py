class WrappedIndicator:
    def __init__(self, to_next_impl, indicators):
        """

        :param to_next_impl: a function in the shape of (bar:Bar,indicator_values:dict)
                            and should return the calculated indicator value.
                            indicator_values is determined by what you passed in for the param `indicators`
        :param indicators: Base Indicators constructed by `BI` , which should be passed in dict
        """
        self.to_next_impl = to_next_impl
        self.indicators = indicators
        self.line = []

    def to_next(self, bar):
        indicator_values = {}
        for name, indicator in self.indicators.items():
            indicator_values[name] = indicator.to_next(bar)
            if indicator_values[name] is None:
                self.line.append(None)
                return None

        res = self.to_next_impl(bar, indicator_values)
        self.line.append(res)
        return res


class BaseIndicator:
    def __init__(self, impl, args, name=None):
        """

        :param impl: `impl` should be a standard Indicator instance,but not a class
        :param args: A list which means the data argument got from the bar
        """
        for arg in args:
            assert arg in ['ask_open', 'ask_close', 'ask_high', 'ask_low', 'bid_open', 'bid_close', 'bid_high',
                           'bid_low',
                           'volume'], "Args should in bar!"

        self.args = args
        self.impl = impl
        self.name = name

    def __repr__(self):
        return self.name

    @property
    def line(self):
        return self.impl.line

    @property
    def lines(self):
        return self.impl.lines

    def to_next(self, bar):
        data_list = []
        for arg in self.args:
            data_list.append(bar.__getattribute__(arg))
        return self.impl.to_next(*data_list)
