# Entry Point of our new trader
# 这个模块的主要目的是获取命令行参数并且调用相应的工具进行回测
import datetime
import os
import traceback

import click
import pandas as pd
import prettytable as pt

import util
import quotation
import runner
from indicator import parseTechniqueStrict

import sys


# We append strategy dir.
sys.path.append('./strategies')


@click.command()
@click.option('-b', '--bundle', default='ratio', help="History Data Bundle")
@click.option('-s', '--strategy', default='range', help="strategy Module")
@click.option('-S', '--start_datetime', default='2012-01-01', help="start date")
@click.option('-E', '--end_datetime', default='2019-01-01', help="start date")
@click.option('-I', '--initial_cash', default=10000, help="initial cash", type=float)
@click.option('-C', '--commission_rate', default=0, help="commission rate", type=float)
@click.option('-O', '--output_file', default=None, help=" select an output file to save the result data in HDF format."
                                                        "In default,we will save as "
                                                        "data/results/backtest-YYYY-MM-DD-HH-mm-ss.h5"
              )
@click.option(
    '-D',
    '--defines',
    multiple=True,
    help="Define a name to be bound in the namespace before executing"
         " the algotext. For example '-D name=value'. The value may be any python"
         " expression. These are evaluated in order so they may refer to previously"
         " defined names.",
)
@click.option('-t', '--technique', default=None, type=str,
              help=" Use Technique Strict, format is low < Indicator_name < High",
              multiple=True)
@click.option('-f', '--frequency', default=None, type=str)
@click.option('-i', '--instrument', default=None, help='instrument,default is to be set by the strategy')
def main(bundle, strategy, start_datetime, end_datetime, initial_cash, commission_rate, output_file, defines,
         instrument, frequency, technique):
    str_module = __import__(strategy)

    param_dict = {}

    for define in defines:
        key, value = define.split('=')
        value = eval(value)
        param_dict[key] = value

    """[summary]
        加载行情数据
        注意： 行情数据从本地配置
    """
    qt = quotation.LocalQuotation()

    ctx = runner.Context(quotation=qt, initial_cash=initial_cash, commission_rate=commission_rate,
                         start_date=start_datetime,
                         end_date=end_datetime)
    # intialize the context
    str_module.init(ctx)

    if instrument is not None:
        if util.forex.is_supported(instrument):
            ctx.instrument = instrument
        else:
            print(' warning: Invalid instrument specified.Use the default setting by the strategy')

    if frequency is not None:
        if frequency in quotation.frequency.supported:
            ctx.frequency = frequency
        elif ctx.frequency is not None:
            print('waring: Invalid frequency specified.Use the default setting by the strategy')
        else:
            ctx.frequency = '1D'
            print('warning: Invalid frequency specified.Use the default of 1D')

    technique_list = []

    if technique is not None:
        for t in technique:
            ti = parseTechniqueStrict(t)
            technique_list.append(ti)
            ctx.parameters_instance[ti["indicator"].name] = f'({ti["low"]},{ti["high"]})'

    for key, param in ctx.parameters.items():
        if key in param_dict:
            assert param.check_valid(param_dict[key]), f'Should low= {param.low} <=value= ' \
                f'{param_dict[key]} < high= {param.high}'
            ctx.parameters_instance[key] = param_dict[key]
        else:
            ctx.parameters_instance[key] = param.default_value

    print('Parameters:')

    tb = pt.PrettyTable(['param', 'value'])
    tb.align["param"] = 'l'
    tb.align["value"] = 'r'
    tb.padding_width = 5
    tb.hrules = pt.ALL
    ctx.parameters_instance['str_name'] = ctx.str_name
    ctx.parameters_instance['start_datetime'] = ctx.start_date
    ctx.parameters_instance['end_datetime'] = ctx.end_date
    ctx.parameters_instance['instrument'] = ctx.instrument
    ctx.parameters_instance['period'] = ctx.frequency
    ctx.parameters_instance['commission_rate'] = ctx.commission_rate
    ctx.parameters_instance['initial_cash'] = ctx.initial_cash
    for key, param in ctx.parameters_instance.items():
        tb.add_row([key, param])

    print(tb)

    print('Loading Quotation...')

    qt.load(ctx.instrument, ctx.frequency, start_datetime, end_datetime, bundle)

    bt = runner.BackTestRunner(str_module, ctx)

    print('Start to run backtest.')

    bt.attach_techniques(technique_list)
    bt.run()
    r = bt.conclude()

    print('Backtest finished.')

    if not r:
        print('No Trade Was Made,So No Result Will be Output.')
        return False

    units = {
        "win_rate": "%",
        "net_ret": "%",
        "max_drawdown": "%"
    }

    round_i = {
        "win_rate": 2,
        "net_ret": 2,
        "max_drawdown": 2,
        "sharp_ratio": 4,
        "plr": 4,
    }

    tb = pt.PrettyTable(['Cost Function', 'Value'])
    tb.align["Cost Function"] = 'l'
    tb.align["Value"] = 'r'
    tb.padding_width = 5
    tb.hrules = pt.ALL
    print('backtest result:')
    for key, value in bt.cost_functions.items():

        u = ''

        if key in units:
            u = units[key]
        v = value
        if key in round_i:
            v = round(v, round_i[key])
        tb.add_row([key, f'{v}{u}'])

    print(tb)

    if output_file is None:
        output_file = os.path.join('data', 'results',
                                   'backtest-%s.h5' % (datetime.datetime.now().strftime('%Y-%m-%d_%H:%m:%S')))

    try:
        with pd.HDFStore(output_file) as hdf:
            hdf.put('trades', bt.trade_df)
            hdf.put('pnl', bt.pnl)
            hdf.put('params', pd.DataFrame([ctx.parameters_instance]))
            hdf.put('cost_functions', pd.DataFrame([bt.cost_functions]))
            print(f'result has been saved to {output_file}')
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    main()
