class Quotation:
    def __init__(self,instrument,frequency):
        self.instrument = instrument
        self.frequency = frequency
    def load(self):
        raise NotImplementedError("Load Quotation is not implemented")
    def next(self,timeout=-1):
        """[summary]
            Should Return the next one quotation in synchron.
            When timeout is hit,should raise the TimeoutException.
        Raises:
            NotImplementedError: [description] This method should not be called directly.
        """
        raise NotImplementedError("Next Quotation is not implemented")
    def async_next(self,callback):
        """[summary]
            Should Return the next one quotation in async mode.
            The Argument is callack function.
        Arguments:
            callback {function} -- [description]
        
        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError("Async Next Quotation is not implemented")