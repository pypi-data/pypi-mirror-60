cdef class SMA:
    cdef readonly int period
    cdef public list line
    cdef list window
    cdef public float temp

    def __init__(self, int period):
        self.period = period
        self.line = []
        self.window = []
        self.temp = 0.0

    def to_next(self, float new_price):
        #574 ms ± 3.47 ms per loop (mean ± std. dev. of 7 runs, 250W loop each)
        cdef float last, result
        self.temp += new_price
        self.window.append(new_price)
        if len(self.window) < self.period:
            self.line.append(None)
            return None
        else:
            last = self.window.pop(0)
            result = self.temp / float(self.period)
            self.temp -= last
            self.line.append(result)
            return result

export = SMA