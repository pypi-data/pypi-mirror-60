from runner.context cimport Context
from runner.context import Context
from broker.local import LocalBroker
from broker.local cimport LocalBroker
from trade.trade cimport Trade
from quotation.bar cimport Bar
from quotation.bar import Bar
from runner.technique cimport Technique
from runner.technique import Technique

cdef class BacktestRunnerImpl:
    cdef Context ctx
    cdef object str_module
    cdef LocalBroker broker
    cdef list techniques
    def __cinit__(self, object str_module, Context ctx):
        self.str_module = str_module
        self.ctx = ctx

        self.broker = LocalBroker(ctx.commission_rate, ctx.initial_cash)

        self.ctx.broker = self.broker

        self.techniques = []

    def attach_technique(self, Technique technique):
        self.techniques.append(technique)
    def attach_techniques(self, list techniques):
        self.techniques += techniques

    def check_technique(self, Bar bar):
        cdef Technique t
        for t in self.techniques:
            if not t.check(bar):
                return False
        return True

    cpdef public void run(self):
        cdef Bar bar,last_bar,bar_p,last_bar_p
        cdef Trade trade
        assert self.ctx.quotation.loaded, "Data Must be Loaded"

        last_bar_p = None

        it = iter(self.ctx.quotation.bar)
        bar =(next(it))
        last_bar = None
        try:
            for bar_p in self.ctx.quotation.bar_p:
                trade = None


                # if last_bar_p is not None and self.check_technique(last_bar_p):
                if last_bar_p is not None and self.check_technique(last_bar_p):
                    trade = self.str_module.on_new_bar_periodically(
                        self.ctx, last_bar_p, ask_open=bar_p.ask_open, bid_open=bar_p.bid_open)

                if trade is not None:
                        # 提交订单以开始的时间为准
                        self.broker.submit_trade(trade, bar_p.start)

                # 单是下在这个周期开始的时间的，那么理论上这个周期内之后的所有分钟数据都可以使用
                # 但是需要注意一下；
                # 对于这个周期内的第一个分钟，只有在整个Bar 都满足成交条件才能成交
                # 对于后面的Bar，则是仅仅需要最高价（或者最低价满足成交条件）
                # 并且前面一个Bar没有达到成交条件。



                # 上一个Bar必须被清空。。


                # 如果分钟远远没有达到这个周期的时间，就过一下
                while bar.start <bar_p.start:
                    bar = next(it)

                last_bar = None

                self.broker.on_bar_p_start(bar)

                while bar_p.start <= bar.start and bar.end <=bar_p.end:
                    self.broker.on_bar(last_bar, bar)

                    last_bar = bar
                    bar = next(it)
                # when the loop is end,the minute is going to be in the next period, or the quotation length.



                # anyway,we close the trade. We don't care about the result.
                # When close the trade, we use the data of the last bar , because the trade should be closed before the
                # period is end.
                self.broker.close_trade(last_bar)

                if self.broker.cash <= 0:
                    # You are broken now.
                    break

                last_bar_p = bar_p
        except StopIteration:
            return
