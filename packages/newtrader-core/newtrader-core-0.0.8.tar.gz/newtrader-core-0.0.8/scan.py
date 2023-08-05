import click
import os
import datetime
import quotation
import runner

import pandas as pd
import traceback
import itertools

import util.forex

import sys

def save_results(param_dict, fixed_param_dict, ctx, results, filename):
    res_df = pd.DataFrame(results)
    res_df = res_df.sort_values(by="sharp_ratio", ascending=False)
    print(res_df)

    meta_info = pd.DataFrame([{
        "str_name": ctx.str_name,
        "frequency": ctx.frequency,
        "instrument": ctx.instrument,
        "initial_cash": ctx.initial_cash,
        "commission_rate": ctx.commission_rate,
        "start_datetime": ctx.start_date,
        "end_datetime": ctx.end_date
    }])

    mutable_params = list(param_dict.keys())
    fixed_params = list(fixed_param_dict.keys())

    for param in mutable_params:
        if param in fixed_params:
            mutable_params.remove(param)

    mutable_params = pd.DataFrame({
        'names': mutable_params,
    })

    all_params = pd.DataFrame({
        'names': list(ctx.parameters.keys())
    })

    if filename is None:
        filename = os.path.join('data', 'results',
                                'scan-%s.h5' % (datetime.datetime.now().strftime('%Y-%m-%d_%H:%m:%S')))
    try:
        res_df.to_hdf(filename, 'result')
        meta_info.to_hdf(filename, 'meta')
        mutable_params.to_hdf(filename, 'mutable_params')
        all_params.to_hdf(filename, 'all_params')
        print(f'result has been saved to {filename}')
    except Exception:
        traceback.print_exc()


def process_params(ranges, defines):
    param_dict = {}
    fixed_param_dict = {}

    for define in ranges:
        key, value = define.split('=')
        value = int(value)
        param_dict[key] = value

    for define in defines:
        key, value = define.split('=')
        value = eval(value)
        fixed_param_dict[key] = value

    return param_dict, fixed_param_dict


def generate_params(ctx, param_dict, fixed_param_dict):
    instances = dict()
    instances['initial_cash'] = [ctx.initial_cash]
    instances['instrument'] = [ctx.instrument]
    instances['commission_rate'] = [ctx.commission_rate]

    # 在instance里面生成一组参数
    for key, param in ctx.parameters.items():
        if key in fixed_param_dict:
            # 首选项： 如果有固定的参数，我们一定把它设置为固定的。
            instances[key] = [fixed_param_dict[key]]
        elif key in param_dict:
            instances[key] = param.generate(param_dict[key])
        else:
            instances[key] = [param.default_value]
    return instances


def product_params(instances):
    # 考虑把他们都乘起来

    for key, values in instances.items():
        instances[key] = [(key, v) for v in values]

    #
    # 这里的结构是： [((k1,v1_1),(k2,v2_1),...),((k1,v1_1),(k2,v2_2),...)]
    prod = list(itertools.product(*instances.values()))

    dict_list = []

    for t in prod:
        d = {}
        for e in t:
            k, v = e
            d[k] = v
        dict_list.append(d)

    return dict_list


sys.path.append('./strategies')


@click.command()
@click.option('-b', '--bundle', default='ratio', help="History Data Bundle")
@click.option('-s', '--strategy', default='range', help="strategy Module")
@click.option('-S', '--start_datetime', default='2014-01-01', help="start date")
@click.option('-E', '--end_datetime', default='2018-01-01', help="start date")
@click.option('-I', '--initial_cash', default=10000, help="initial cash", type=float)
@click.option('-C', '--commission_rate', default=0, help="commission rate", type=float)
@click.option('-P', '--process_count', default=None, help="process count, default is cpu count", type=int)
@click.option('-O', '--output_file', default=None, help=" select an output file to save the result data in HDF format."
                                                        "In default,we will save as "
                                                        "data/results/scan-YYYY-MM-DD-HH-mm-ss.h5")
@click.option('-i', '--instrument', default=None, help='instrument,default is to be set by the strategy')
@click.option(
    '-D',
    '--defines',
    multiple=True,
    help="Set fixed values for scanning of the certain parameter before executing"
         " computing . For example '-Dname=value'. The value will be used to fix the parameter you choosed, and the "
         "selected parameters will be removed for the mutable parameters"
)
@click.option(
    '-R',
    '--ranges',
    multiple=True,
    help="Set range for scanning of the certain parameter before executing"
         " computing . For example '-R name=value'. the value should be integers "
         "which times you want to calculate repeatedly for "
         " the certain parameter"
)
@click.option('-f', '--frequency', default=None, type=str)
def main(bundle, strategy, start_datetime, end_datetime, initial_cash, commission_rate, ranges, process_count,
         output_file, defines, instrument, frequency):
    str_module = __import__(strategy)

    param_dict, fixed_param_dict = process_params(ranges, defines)

    """[summary]
        加载行情数据
        注意： 行情数据从本地配置
    """
    qt = quotation.LocalQuotation()

    ctx = runner.Context(quotation=qt, initial_cash=initial_cash, commission_rate=commission_rate,
                         start_date=start_datetime, end_date=end_datetime)

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

    qt.load(ctx.instrument, ctx.frequency, start_datetime, end_datetime, bundle)

    instances = generate_params(ctx, param_dict, fixed_param_dict)

    dict_list = product_params(instances)

    print('start to scan')

    try:
        results = runner.run_scan(strategy, ctx, dict_list, process_count)

        save_results(param_dict, fixed_param_dict, ctx, results, output_file)

    except Exception:
        traceback.print_exc()
    finally:
        qt.close_share()


if __name__ == '__main__':
    main()
