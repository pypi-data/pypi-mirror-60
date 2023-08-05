"""[summary]
BacktestRunner的职责：
1. 根据数据源，构造中间商。
2. 实体化策略。
3. 在for-loop中回测策略
4. 【可选】分析策略，给出策略报表

我们希望这个能被更高级的（比如批量枚举的Runner给复用。
"""

from broker import LocalBroker
from runner import bt_impl
from runner.technique import Technique
import pandas as pd
import numpy as np

import math


def sharp_ratio(d):
    d = d.dropna()
    d = d.set_index('entry_datetime')
    profit = d['profit']
    profit = profit.resample('1D').sum()
    profit = profit[profit != 0]
    profit = np.asarray(profit)

    volatility = profit.std(ddof=1)

    if volatility != 0:
        avg_returns = profit.mean()
        return (avg_returns / volatility) * math.sqrt(252)
    else:
        return 0


def win_rate(d):
    d = d.loc[:, ['profit']]
    win = d[d['profit'] > 0].count()
    loss = d[d['profit'] < 0].count()

    return (win / (win + loss) * 100)['profit']


def plr(d):
    d = d.loc[:, ['profit']]
    win = d[d['profit'] > 0].mean()
    loss = d[d['profit'] < 0].mean().abs()
    return (win / loss)['profit']


def net_ret(d, initial_cash):
    ret_cash = d['profit'].sum()
    return ret_cash / initial_cash * 100


def max_drawdown(pnl):
    rec = list(pnl.items())
    last_max_time, last_max_value = rec[0]

    max_drawdown = 0
    max_drawdown_duration = np.timedelta64(0)

    for time, value in rec:
        if last_max_value < value:
            last_max_time = time
            last_max_value = value
        if last_max_value > value:
            dd = (last_max_value - value) / last_max_value
            if dd > max_drawdown:
                max_drawdown = dd
                ddd = time - last_max_time
                if ddd > max_drawdown_duration:
                    max_drawdown_duration = ddd
    return max_drawdown * 100, max_drawdown_duration


def conclude_from_trades(trade_df, initial_cash):
    df = trade_df.set_index('id')

    d = df.set_index('exit_datetime')
    d = d.dropna()
    pnl = d['profit'].cumsum() + initial_cash

    cost_functions = {}
    cost_functions['sharp_ratio'] = sharp_ratio(
        df)
    cost_functions['win_rate'] = win_rate(df)
    cost_functions['plr'] = plr(df)
    cost_functions['net_ret'] = net_ret(df, initial_cash)
    cost_functions['trade_count'] = df.shape[0]

    holding = (df['exit_datetime'] - df['entry_datetime'])

    cost_functions['max_holding'] = holding.max()
    cost_functions['min_holding'] = holding.min()
    cost_functions['avg_holding'] = holding.mean()
    cost_functions['std_holding'] = holding.std(ddof=0)
    cost_functions['max_drawdown'], cost_functions['max_drawdown_duration'] = max_drawdown(
        pnl)
    return df, pnl, cost_functions


class BackTestRunner:

    def __init__(self, str_module, ctx):
        """[summary]

        Arguments:
            str_module {[module]} -- [description]
            quotation {[Quotation]} -- [description]
            param_dict {[dict]} -- [description]
        """

        self.impl = bt_impl.BacktestRunnerImpl(str_module=str_module, ctx=ctx)

        self.str_module = str_module
        self.ctx = ctx

        self.trade_df = None
        self.cost_functions = None
        self.pnl = None
        self.techniques = []

    def attach_technique(self, t):
        self.impl.attach_technique(Technique(indicator=t["indicator"], low=t["low"], high=t["high"]))

    def attach_techniques(self, tl):
        techniques = []
        for t in tl:
            techniques.append(Technique(indicator=t["indicator"], low=t["low"], high=t["high"]))

        self.impl.attach_techniques(techniques)

    def run(self):
        self.impl.run()

    def conclude(self):

        broker = self.ctx.broker

        df = pd.DataFrame([trade.to_dict() for trade in broker.trades])
        if df.shape[0] == 0:
            return False
        df['submit_datetime'] = pd.to_datetime(df['submit_datetime'], unit='m')
        df['entry_datetime'] = pd.to_datetime(df['entry_datetime'], unit='m')
        df['exit_datetime'] = pd.to_datetime(df['exit_datetime'], unit='m')
        df = df[df['state'] != 3]
        self.trade_df, self.pnl, self.cost_functions = conclude_from_trades(df, broker.initial_cash)
        return True
