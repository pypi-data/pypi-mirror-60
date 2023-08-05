
cdef convert_bar_to_sgn(float open, float close):
    if open > close:
        return -1
    if open < close:
        return 1
    else:
        return 0

cdef class RSI:
    cdef readonly int period
    cdef public list line
    cdef float up
    cdef float down
    cdef list window

    def __init__(self, period):
        self.up = 0
        self.down = 0
        self.window = []
        self.line = []
        self.period = period
    def to_next(self, float new_open, float new_close):

        cdef float rs = 0.0, rsi = 0.0
        cdef float last = 0
        cdef float delta = 0

        delta = new_close - new_open

        if delta > 0:
            self.up += delta
        else:
            self.down += -delta

        self.window.append(delta)

        if len(self.window) < self.period:
            self.line.append(None)
            return None
        else:
            last = self.window.pop(0)
            rs = self.up + self.down
            if rs > 0:
                rsi = self.up / rs
            else:
                self.line.append(None)
                return None
            ## 只考虑多少两种情况
            if last > 0:
                self.up -= last
            else:
                self.down -= -last
            self.line.append(rsi)
            return rsi

export = RSI
