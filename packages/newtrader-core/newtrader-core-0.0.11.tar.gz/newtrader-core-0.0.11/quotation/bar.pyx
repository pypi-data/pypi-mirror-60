from numpy cimport float64_t, ndarray
from numpy import ndarray
import ctypes

cdef class Bar:
    def __cinit__(self, ndarray[float64_t] array):
        self.ask_open= array[2]
        self.ask_high= array[3]
        self.ask_low= array[4]
        self.ask_close= array[5]
        self.bid_open= array[6]
        self.bid_high= array[7]
        self.bid_low= array[8]
        self.bid_close= array[9]
        self.volume= array[10]
        self.start= array[0]
        self.end= array[1]
