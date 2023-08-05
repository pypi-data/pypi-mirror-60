from trade.trade cimport Trade, Direction,OrderType
from runner import Parameter

cimport numpy as np
from runner.context cimport Context
from quotation.bar cimport Bar

cpdef void init(Context ctx):
    # 这里可以指定交易的标的类型
    ctx.instrument = 'EURUSD'
    ctx.str_name = '趋势策略-做空'
    # 这里指定交易的频率（周期）
    ctx.frequency = '1D'

    #   不论是在优化还是回测，或者实盘运行中，init总共都只会被调用一次。
    #   在这里可以用Parameter类设置参数的最小值，最大值，默认值。
    #   1. 优化扫描时，将在最小和最大值之间按照调用程序设定的步长进行扫描。
    #   2. 回测和实际运行时， 如果调用者没有给出该参数的值，那么参数取默认值。

    ctx.parameters = {
        "k": Parameter(2, 0, 0.131),
        "t": Parameter(0.100, 0, 0.0070),
        "s": Parameter(0.100, 0, 0.0050),
        "quantity": Parameter(9999999999999, 0, 1),
    }

cpdef void on_new_bar(Context ctx, Bar bar):
    """[summary]
        In this function ,you can collect data by bars and do something.
    Arguments:
        ctx {[type]} -- [description]
        bar {[type]} -- [description]
    """

    pass

cpdef Trade on_new_bar_periodically(Context ctx, Bar last_bar, np.float64_t ask_open, np.float64_t bid_open):
    """[summary]
        在这个函数中，你可以根据上一个周期的数据以及当前周期开始的数据来判断你是否需要进行交易

        如果交易，按照下面的方式返回一个Trade即可
        如果不交易，那么返回None


    Arguments:
        ctx {[type]} -- [description]
        last_bar {[type]} -- [description]
        current_bar {[type]} -- [description]
    
    Returns:
        [type] -- [description]
    """
    cdef np.float64_t range_0
    cdef np.float64_t in_price, out_price, stop_price

    range_0 = last_bar.ask_high - last_bar.ask_low
    in_price = bid_open - range_0 * ctx.parameters_instance["k"]
    out_price = in_price - ctx.parameters_instance["t"]
    stop_price = in_price + ctx.parameters_instance["s"]

    # 下面以做多为例说明Trade的参数
    # 第一个参数是标的的类型，必须和你前面指定的一致
    # 第二个参数是入场价格，当你进行做多的时候，只有价格比这个低才会入场
    # 第三个参数是止损价格，当入场后价格跌破这个价格，那么会帮你止损出场（平仓）
    # 第四个是目标出场价格，当入场后价格超过这个价格的时候，会平仓止盈
    # 第五个参数是交易方向， BUY是做多， SELL 是做空

    # 如果一个周期内没有限价出场，也没有止损，那么在周期结束之前会以市价单的方式强行平仓
    return Trade(ctx.instrument, in_price, stop_price, out_price, ctx.parameters_instance["quantity"], Direction.SELL,
                 entry_type=OrderType.Stop)
