from quotation import LocalQuotation
from indicator import analyzer

import click
import tqdm
import traceback

import pandas as pd


@click.command()
@click.option('-i', '--input', help="Input File,which is a backtest result")
@click.option('-o', '--output', help="Output File,which should be a file with jpg/png ext.")
@click.option('-b', '--bundle', help='Quotation Data bundle.', default='ratio')
@click.option('-l', '--indicator_list', help='技术指标列表。用于说明如何生成技术指标。由XML格式所决定', default='indicators.xml')
def main(input, output, bundle, indicator_list):
    with pd.HDFStore(input) as bt_hdf:
        try:
            trades = bt_hdf.get('trades')
            params = bt_hdf.get('params')
            params = params.loc[0, :]
            instrument = params["instrument"]
            start_datetime = params["start_datetime"]
            end_datetime = params["end_datetime"]
            period = params["period"]

        except KeyError as k:
            print(f'Bad Input,occur key error:{k}')
            return
    try:
        ilist = analyzer.parseXMLToIndicators(indicator_list)
    except Exception:
        print(f'parse Indicator List XML :{indicator_list} Failed. Error is below ')
        traceback.print_exc()
        return
    try:
        quotation = LocalQuotation()
        quotation.load(start=start_datetime, end=end_datetime, bundle=bundle, instrument=instrument, frequency=period,
                       period_only=True)
    except Exception:
        print(
            f'Load quotation failed,time:[{start_datetime},{end_datetime}],'
            f'bundle={bundle},instrument={instrument},frequency={period}. Error is below')
        traceback.print_exc()
        return

    print('start to calculate')

    t = tqdm.tqdm(total=len(ilist), unit='indicator')

    def _update(t):
        return lambda: t.update(1)

    res = []

    for i in ilist:
        res1 = analyzer.analyze_instance(i=i, qt=quotation, trades=trades)
        res.append(res1)
        t.update(1)
    t.close()

    print('start to plot')

    t = tqdm.tqdm(total=len(res), unit='indicator')

    path = analyzer.plot_cumcurves(output, res, callback=_update(t))
    t.close()

    print(f'saved to {path}')


# qt.load(bundle = bundle)

if __name__ == '__main__':
    main()
