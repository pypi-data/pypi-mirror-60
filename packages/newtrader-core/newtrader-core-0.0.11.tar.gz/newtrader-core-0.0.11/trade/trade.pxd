cimport numpy as np
cpdef enum Direction:
    BUY = 1
    SELL = -1

cpdef enum State:
    INITIAL = 0
    ENTRIED = 1
    EXITED = 2
    CANCELLED = 3

cpdef enum OrderType:
    Limit = 0
    Market = 1
    Stop = 2
    INVALID = -1

cdef class Trade:
    cdef readonly  int id
    cdef readonly  str instrument
    cdef readonly  np.float64_t entryPrice
    cdef readonly  np.float64_t stopLossPrice
    cdef readonly  np.float64_t profitTargetPrice
    cdef readonly  int quantity
    cdef readonly  object submit_datetime
    cdef readonly  object exit_datetime
    cdef readonly object entry_datetime
    cdef readonly np.float64_t exit_price
    cdef readonly  Direction direction
    cdef readonly  np.float64_t commission_rate
    cdef readonly  np.float64_t commission
    cdef readonly  np.float64_t profit # 设定后会自动扣除手续费
    cdef readonly OrderType entry_type
    cdef readonly  OrderType exit_type
    cdef readonly  State state

