from .base import Broker
from trade.trade cimport State, Trade, OrderType, Direction
from trade.trade import Trade
from quotation.bar cimport Bar
from quotation.bar import Bar
import numpy as np
from broker.execute_local import execute_limit_order_s, execute_limit_order, execute_market, execute_stop_order_s, \
    execute_stop_order,execute_els_order
from util.forex import point_rate

# 根据交易细节断定能不能成交
cdef inline float calculate_profit(float exit_price, float entry_price, float quantity, Direction direction,
                                   str instrument):
    return (exit_price - entry_price) * quantity * point_rate[
        instrument] * direction

cdef class LocalBroker:
    def __init__(self, float commission_rate=0.0, float initial_cash=1000.0):
        """[summary]
            This local broker only supports single trade mode.
            Every method of the local broker should be called only by the runner, which means you should
            ensure everything works as the real trading envrionment。
            So this api is not useful for user level of `newtrader`.

            Every action,such as submit/exit trades should be provided with the accurate context data including quotation and datetime.

            It‘s not neccessary for it to be provided with the quotation in the initialization funciton.

            In fact, when trading online, quotation is provided by the broker itself, which means it;s not our bussiness.

        
        Keyword Arguments:
            commission_rate {float} -- [description] (default: {0.0})
            initial_cash {float} -- [description] (default: {1000.0})
        """
        self.trade_id = 0
        self.trades = []

        self.commission_rate = commission_rate

        self.initial_cash = initial_cash
        self.cash = initial_cash

        self.current_trade = None

    def submit_trade(self, Trade trade, object datetime):
        """[summary]
            我们把这个交易提交到做市商
        Arguments:
            trade {[Trade]} -- [description] 要提交的交易
        """

        trade.accept(datetime, self.trade_id)
        self.trade_id += 1

        self.trades.append(trade)
        self.current_trade = trade
    def close_trade(self, Bar bar):
        """[summary]
            Close the current trade.

            Exit market when entered, else cancel it.
        Arguments:
            last_bar {[type]} -- [description]
            bar {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        cdef float profit

        if self.current_trade is None:
            return False

        assert self.current_trade.state in [State.INITIAL,
                                            State.ENTRIED], f'Trade [{self.current_trade.id}] cannot be closed.'

        if self.current_trade.state == State.INITIAL:
            self.current_trade.cancel()
        else:
            price = execute_market(bar=bar, direction=self.current_trade.direction * (-1))
            profit = calculate_profit(exit_price=price, entry_price=self.current_trade.entryPrice,
                                      direction=self.current_trade.direction,
                                      quantity=self.current_trade.quantity,
                                      instrument=self.current_trade.instrument)
            self.current_trade.exit(exit_price=price, profit=profit, exit_type=OrderType.Market, at=bar.start)
            self.cash += self.current_trade.profit

        self.current_trade = None

        return True

    # 每个周期开始时第一个Bar的处理
    def on_bar_p_start(self, Bar bar):
        cdef float price
        price = -1
        if self.current_trade is not None:
            if self.current_trade.entry_type == OrderType.Limit:
                price = execute_limit_order_s(bar, self.current_trade.direction, self.current_trade.entryPrice)
            if self.current_trade.entry_type == OrderType.Stop:
                price = execute_stop_order_s(bar, self.current_trade.direction, self.current_trade.entryPrice)
        if price > 0:
            self.current_trade.entry(entryPrice=price, at=bar.start)
    def on_bar(self, Bar last_bar, Bar bar):
        cdef float profit

        if self.current_trade is None:
            return

        if self.current_trade.state == State.INITIAL:
            if self.current_trade.entry_type == OrderType.Limit:
                price = execute_limit_order(last_bar, bar, self.current_trade.direction, self.current_trade.entryPrice)
            if self.current_trade.entry_type == OrderType.Stop:
                price = execute_stop_order(last_bar, bar, self.current_trade.direction, self.current_trade.entryPrice)
            if price > 0:
                self.current_trade.entry(entryPrice=price, at=bar.start)

        if self.current_trade.state == State.ENTRIED:
            # 出场的时候和入场的方向相反
            price, type = execute_els_order(last_bar=last_bar, bar=bar, direction=self.current_trade.direction * (-1),
                                            stop_price=self.current_trade.stopLossPrice,
                                            limit_price=self.current_trade.profitTargetPrice)
            if price > 0:
                profit = calculate_profit(exit_price=price, entry_price=self.current_trade.entryPrice,
                                          direction=self.current_trade.direction,
                                          quantity=self.current_trade.quantity,
                                          instrument=self.current_trade.instrument)
                self.current_trade.exit(exit_price=price, profit=profit, exit_type=type, at=bar.start)
                self.current_trade = None
