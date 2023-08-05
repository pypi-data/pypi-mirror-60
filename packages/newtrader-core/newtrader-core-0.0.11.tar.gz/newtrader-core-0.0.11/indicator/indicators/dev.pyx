import numpy as np
cimport numpy as np

cdef class Dev:
    cdef np.ndarray window
    cdef int dof
    cdef int current
    cdef int window_size
    cdef readonly list line
    def __init__(self, int window_size, int dof):
        self.dof = dof
        self.window_size = window_size
        self.window = np.empty(dtype=np.float32, shape=(window_size,))
        self.current = 0
        self.line = []
    def to_next(self, float value):
        cdef float std
        if self.current < self.window_size:
            self.window[self.current] = value
            self.current += 1
            if self.current == self.window_size:
                std = np.std(self.window, ddof=self.dof)
                self.line.append(std)
                return std
            else:
                self.line.append(None)
                return None

        self.window[self.current % self.window_size] = value
        std = np.std(self.window, ddof=self.dof)
        self.line.append(std)
        return std

export = Dev
