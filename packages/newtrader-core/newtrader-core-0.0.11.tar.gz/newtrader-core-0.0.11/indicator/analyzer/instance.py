from quotation import LocalQuotation
from indicator import BaseIndicator
from algo import max_interval
import pandas as pd


def max_cumsum_interval(cumsum):
    max_i, min_i, max_up = max_interval.max_delta_interval(cumsum['profit'].to_list())
    return cumsum.index[min_i], cumsum.index[max_i], max_up


def analyze_instance(i: BaseIndicator, qt: LocalQuotation, trades: pd.DataFrame):
    """

    :param i: 技术指标实例
    :param qt:  行情数据
    :param trades: 交易列表
    :return:
    """
    for bar in qt.bar_p:
        i.to_next(bar)

    submit_table = trades.set_index('submit_datetime')

    indicator_df = pd.DataFrame(index=qt.df_p.index.copy().rename('submit_datetime'), data={i.name: i.line}).shift(
        periods=1)

    # 得到列联表
    # 这里是 把Indicator和订单表连接起来，索引是提交的时间
    joined_trade = submit_table.join(indicator_df)
    # 累计求和
    cumsum = joined_trade.groupby(i.name).sum().dropna(how='any').cumsum()

    start_v = 0.0
    end_v = 0.0

    if cumsum.shape[0] > 0:

        start_v, end_v, max_up = max_cumsum_interval(cumsum)

        filtered_trade = \
            joined_trade[(joined_trade[i.name] > start_v) & (joined_trade[i.name] < end_v)]
    else:
        filtered_trade = joined_trade

    filtered_trade[['exit_datetime', 'profit']].rename(columns={'exit_datetime': 'DateTime'}).set_index('DateTime').cumsum()
    exited = filtered_trade[['exit_datetime', 'profit']].rename(columns={'exit_datetime': 'DateTime'}).set_index(
        'DateTime').cumsum()
    submit = filtered_trade[['profit']]
    submit.index = submit.index.rename('DateTime')
    submit = submit.cumsum().shift(1).dropna()
    exited = exited.loc[exited.index.dropna()]
    result_pnl = submit.merge(exited, how='outer', on=['DateTime', 'profit'])
    result_pnl = result_pnl.sort_index()

    return i.name, start_v, end_v, result_pnl, cumsum, indicator_df
