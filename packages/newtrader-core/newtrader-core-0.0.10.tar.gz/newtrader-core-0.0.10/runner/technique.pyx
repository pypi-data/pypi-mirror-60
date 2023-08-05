from quotation.bar cimport Bar

cdef class Technique:
    def __cinit__(self, object indicator, float low, float high):
        self.indicator = indicator
        self.low = low
        self.high = high
    def check(self, Bar bar):
        cdef object v
        v = self.indicator.to_next(bar)
        return v is not None and self.low <= v <= self.high
