cdef class EMA:
    cdef readonly int period
    cdef public list line
    cdef float k
    def __init__(self, int period):
        self.period = period
        self.line = []

        self.k = 2.0 / (period + 1)

    def to_next(self, float new_price):
        #574 ms ± 3.47 ms per loop (mean ± std. dev. of 7 runs, 250W loop each)
        cdef float result
        if len(self.line) == 0:
            self.line.append(new_price)
            return new_price
        else:
            result = new_price * self.k + self.line[-1] * (1 - self.k)
            self.line.append(result)
            return result

export = EMA
