import numpy as np

# cdef class Parameter:
#     def __init__(self, float high, float low, float default):
#         self.high = high
#         self.low = low
#         self.default = default
#         assert self.low <= self.default < self.high, f'Should low= {low} <=default= {default} < high= {high}'
#
#     def check_valid(self, float value):
#         return self.low <= value < self.high
#
#     def generate(self, int num):
#         return np.linspace(self.low, self.high, num)


cdef class Context:
    def __cinit__(self,object quotation=None,str instrument="",float initial_cash=0.0,float commission_rate=0.0,
                    object start_date=None,object end_date=None,str frequency='1D',object broker = None
                 ):
        """[summary]
            Initialize the context and run the result.

        """
        self.instrument = instrument
        self.quotation = quotation

        self.broker = broker

        self.start_date = start_date
        self.end_date = end_date

        self.parameters = {}
        self.parameters_instance = {}

        self.initial_cash = initial_cash
        self.commission_rate = commission_rate

        self.str_name = 'Unamed Stragety'

        self.frequency = frequency
