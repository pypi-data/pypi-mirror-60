cdef class Low:
    cdef readonly int period
    cdef public list line
    cdef list window
    cdef list min

    cdef int current
    # 当前元素在整个序列中的位置

    def __init__(self, int period):
        self.period = period
        self.window = []
        self.line = []
        self.min = []
        self.current = 0

    def to_next(self, float data):
        cdef float res
        self.window.append(data)

        if self.current < self.period - 1:
            # 淘汰上一个最小值

            while len(self.min) > 0 and self.window[self.min[-1] - self.current - 1] >= data:
                self.min.pop(-1)

            # 把当前元素添加上
            self.min.append(self.current)
            self.current += 1
            self.line.append(None)
            return None
        else:
            if len(self.min)>0 and self.min[0] <= self.current - self.period:
                self.min.pop(0)
            while len(self.min) > 0 and self.window[self.min[-1] - (self.current + 1 - self.period)] >= data:
                self.min.pop(-1)
            # 把当前元素添加上
            self.min.append(self.current)
            res = self.window[self.min[0] - (self.current + 1 - self.period)]
            self.window.pop(0)
            self.line.append(res)
            self.current += 1
            return res

export = Low
