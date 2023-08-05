# Now what you only need to do for construct a indicator is to call
# BaseIndicator(RSI(24*60),['ask_close'])
# for a simplified calling: BI(RSI,24*60,['ask_open','ask_close'])
import itertools

from indicator.wrappers import BaseIndicator
from ..indicators import classes


def BI(indicator_class, params, args):
    """
                example:- BI(RSI,24*60,['ask_open','ask_close'])
                        - BI(MACD,[24*60,24*60*5],['ask_open'])
    :param indicator_class:  The class of Indicator
    :param params: params or param use to create instance
    :param args: args or arg passing to `to_next` , you can use either `list` or `dict`
    :return: BaseIndicator,with name in Indicator(param1,param2)[arg1,arg2....] like `RSI(60)[ask_open,ask_close]`
    """
    if type(params) is tuple:
        _params = list(params)
    elif type(params) is not list:
        _params = [params]
    else:
        _params = params

    # 无论如何都换成 list
    if type(args) is tuple:
        _args = list(args)
    elif type(args) is not list:
        _args = [args]
    else:
        _args = args
    instance = indicator_class(*_params)

    param_str = f"({str(_params)[1:-1]})"
    arg_str = f"[{','.join(_args)}]"

    return BaseIndicator(instance, _args, f"{indicator_class.__name__}{param_str}{arg_str}")


def BIG(indicator_class, params_list, args_list):
    indicators = []
    pa_iter = itertools.product(params_list, args_list)
    for params, args in pa_iter:
        indicators.append(BI(indicator_class, params, args))

    return indicators


def BIN(indicator_class_name, params, args):
    assert indicator_class_name in classes.keys(), f'indicator:{indicator_class_name} not exists.'
    return BI(classes[indicator_class_name], params, args)


def BIS(indicator_string: str):
    # TODO: Check the Format
    [name, r] = indicator_string.split('(')
    [params, remain] = r.split(')')
    params = eval(params)
    args = remain.replace('[', '').replace(']', '').split(',')
    return BIN(name, params, args)


def parseTechniqueStrict(technique: str):
    """
        for example : 0.125 < RSI(30)[ask_open,ask_close] < 0.45
    :param technique:
    :return:
    """
    format = technique.split('<')
    indicator = BIS(format[1])
    low = float(format[0])
    high = float(format[2])
    return {
        "low": low,
        "high": high,
        "indicator": indicator
    }
