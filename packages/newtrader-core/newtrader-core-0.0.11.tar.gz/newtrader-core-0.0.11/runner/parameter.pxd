cimport numpy as np
cdef class Parameter:
    cdef readonly np.float64_t low
    cdef readonly np.float64_t high
    cdef readonly np.float64_t default_value
