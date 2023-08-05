cimport numpy as np
cimport quotation.bar
import quotation.bar

cdef class Trade:
    """
        对于 Trade 这个类，它包含了交易的一些信息
        但是我们的设计并不希望他包含执行的逻辑。
        执行的逻辑应该由具体的Broker的配套给出
    """

    def __init__(self, str instrument, np.float64_t entryPrice, np.float64_t stopLossPrice,
                 np.float64_t profitTargetPrice, int quantity,
                 Direction direction, OrderType entry_type):
        # assert type(direction) is Direction
        # 
        # assert (
        #                stopLossPrice - entryPrice) * direction.value <= 0, "Invalid Stop Loss Price:{},with Entry Price:{},direction:{}".format(
        #     stopLossPrice, stopLossPrice, "Buy" if (direction == 1) else "Sell")
        # assert (profitTargetPrice - entryPrice) * direction.value >= 0, "Invalid Targe price"

        self.id = 0
        self.instrument = instrument

        self.entryPrice = round(entryPrice, 5)
        self.stopLossPrice = round(stopLossPrice, 5)
        self.profitTargetPrice = round(profitTargetPrice, 5)
        self.quantity = quantity

        # 关于时间： 我们用最小频率的开始的那个时刻做记录
        self.submit_datetime = None
        self.entry_datetime = None
        self.exit_datetime = None
        self.exit_price = 0

        self.direction = direction

        self.commission_rate = 0
        self.commission = 0

        self.profit = 0.0

        self.entry_type = entry_type
        self.exit_type = OrderType.INVALID
        self.state = State.INITIAL

    def to_dict(self):
        return {
            "id": self.id,
            "instrument": self.instrument,
            "direction": self.direction,
            "entryPrice": self.entryPrice,
            "stopLossPrice": self.stopLossPrice,
            "profitTargetPrice": self.profitTargetPrice,
            "quantity": self.quantity,
            "submit_datetime": self.submit_datetime,
            "entry_datetime": self.entry_datetime,
            "exit_datetime": self.exit_datetime,
            "entry_type": self.entry_type,
            "exit_price": self.exit_price,
            "exit_type": self.exit_type,
            "commission": self.commission,
            "state": self.state,
            "profit": self.profit,
        }

    def set_commission_rate(self, float rate):
        self.commission_rate = rate
        self.commission = rate * self.quantity

    def accept(self, object dt, int ID):
        """[summary]
            Accept the trade to the broker.
            When it's accepted , an ID should be provided.
        Arguments:
            dt {[type]} -- [description]
            ID {[type]} -- [description]
        """
        self.id = ID
        self.submit_datetime = dt

    def cancel(self):
        """[summary]
            If the trade is just initialized,it can be cancelled.

            If cancelled retrun `False`.
            else `True`
        Arguments:
            dt {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        assert self.state == State.INITIAL, f"The trade cannot be exited for that the state for trade " \
                                            f"{self.id}, start at {self.submit_datetime} is {self.state},entering at f{self.entry_datetime}."
        self.state = State.CANCELLED

    def entry(self, float entryPrice, object at):
        self.entryPrice = entryPrice
        self.entry_datetime = at
        self.state = State.ENTRIED
    def exit(self, OrderType exit_type, float exit_price, float profit, object at):
        """[summary]
            由Broker调用，由行情数据判断如何退出市场
        Arguments:
            last_bar {[type]} -- [description]
            bar {[type]} -- [description]

        Returns:
            [type] -- [description]
        """

        self.exit_price = exit_price
        self.exit_datetime = at
        self.profit = profit - self.commission
        self.exit_type = exit_type
        self.state = State.EXITED
