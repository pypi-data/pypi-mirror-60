from trade.trade cimport State, Trade

cdef class LocalBroker:
    cdef readonly list trades
    cdef int trade_id
    cdef readonly float commission_rate
    cdef readonly float initial_cash
    cdef public float cash
    cdef Trade current_trade

