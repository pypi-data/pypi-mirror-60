cimport numpy as np
import numpy as np

cdef class SimpleSlope:
    cdef np.ndarray window
    cdef int length
    cdef int current
    cdef list line
    def __init__(self, int length):
        self.length = length
        self.window = np.empty(dtype=np.float64, shape=(length,))
        self.current = 0
        self.line = []
    def to_next(self, np.float64_t data):
        cdef float slope
        cdef int index

        if self.current < self.length:
            self.window[self.current] = data
            self.current += 1

            if self.current != self.length:
                self.line.append(None)
                return None
            else:
                slope = (data - self.window[0]) / self.length
                self.line.append(slope)
                return slope

        index = self.current % self.length
        self.current +=1

        self.window[index] = data

        slope = (data - self.window[index - self.length+1]) / self.length

        self.line.append(slope)
        return slope
