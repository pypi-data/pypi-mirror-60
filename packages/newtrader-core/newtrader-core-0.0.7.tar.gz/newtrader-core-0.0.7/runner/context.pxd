cimport numpy as np 





cdef class Context:
    cdef public str instrument
    cdef public object quotation
    cdef public object broker
    cdef public object parameters
    cdef public object parameters_instance
    cdef public np.float64_t initial_cash
    cdef public np.float64_t commission_rate
    cdef public str str_name
    cdef public str frequency
    cdef public object start_date
    cdef public object end_date
