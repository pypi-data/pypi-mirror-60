cimport numpy as np
cdef class Bar:
     cdef readonly np.float64_t end
     cdef readonly np.float64_t start
     cdef readonly np.float64_t ask_open
     cdef readonly np.float64_t ask_close
     cdef readonly np.float64_t ask_low
     cdef readonly np.float64_t ask_high
     cdef readonly np.float64_t bid_open
     cdef readonly np.float64_t bid_close
     cdef readonly np.float64_t bid_low
     cdef readonly np.float64_t bid_high
     cdef readonly np.float64_t volume
