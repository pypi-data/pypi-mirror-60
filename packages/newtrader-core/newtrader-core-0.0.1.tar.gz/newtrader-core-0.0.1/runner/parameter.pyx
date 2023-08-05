import numpy as np
cdef class Parameter:
    def __init__(self, float high, float low, float default_value):
        self.high = high
        self.low = low
        self.default_value = default_value

    def check_valid(self, float value):
        return self.low <= value < self.high

    def generate(self, int num):
        return np.linspace(self.low, self.high, num)

