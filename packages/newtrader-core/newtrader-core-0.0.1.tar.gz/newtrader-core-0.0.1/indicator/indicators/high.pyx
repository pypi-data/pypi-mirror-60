cdef class High:
    cdef readonly int period
    cdef public list line
    cdef list window
    cdef list max
    cdef int current
    # 当前元素在整个序列中的位置
    def __init__(self, int period):
        self.period = period
        self.window = []
        self.line = []
        self.max = []
        self.current = 0
    def to_next(self, float data):
        cdef float res
        self.window.append(data)
        if self.current < self.period-1:
            # 淘汰上一个最大值
            while len(self.max) > 0 and self.window[self.max[-1] - self.current - 1] <= data:
                self.max.pop(-1)
            # 把当前元素添加上
            self.max.append(self.current)
            self.current += 1
            self.line.append(None)
            return None
        else:
            if len(self.max) >0 and self.max[0] <= self.current - self.period:
                self.max.pop(0)
            while len(self.max) > 0 and self.window[self.max[-1] - (self.current + 1 - self.period)] <= data:
                self.max.pop(-1)
            # 把当前元素添加上
            self.max.append(self.current)
            res = self.window[self.max[0] - (self.current + 1 - self.period)]
            self.window.pop(0)
            self.line.append(res)
            self.current += 1
            return res

export = High