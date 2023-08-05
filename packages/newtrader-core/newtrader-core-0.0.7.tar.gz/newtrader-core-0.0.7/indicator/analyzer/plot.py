import matplotlib.pyplot as plt
import os
import datetime
import matplotlib.ticker as tk
import matplotlib.dates as mdates  # 處理日期
from matplotlib.backends.backend_pdf import PdfPages


def trim_axs(axs, N):
    """little helper to massage the axs list to have correct length..."""
    axs = axs.flat
    for ax in axs[N:]:
        ax.remove()
    return axs[:N]


def cb():
    pass


def plot_cumcurve(axs, data, callback):
    (name, start_v, end_v, filtered_pnl, cs, indicator_df) = data
    ax1, ax2, ax3 = axs

    ax1.plot(cs.index, cs['profit'], 'o-', color='red', markersize=2, )
    ax1.set_xlabel(name)
    ax1.set_ylabel('Cum Return')
    ax1.set_title(f'{round(start_v,8)}<{name}<{round(end_v,8)}')
    ax1.grid(True)
    ax1.xaxis.set_major_locator(tk.MaxNLocator())
    ax1.axvline(start_v, color='blue', label=start_v)
    ax1.axvline(end_v, color='green', label=end_v)

    ax2.plot(indicator_df.index, indicator_df[name], 'o-', markersize=2, color='red')
    ax2.fmt_xdata = mdates.DateFormatter('%Y-%m')
    ax2.grid(True)
    ax2.set_title('Indicator Series')
    ax2.set_xlabel('Date')
    ax2.set_ylabel(name)
    plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')

    ax3.plot(filtered_pnl.index, filtered_pnl, 'o-', markersize=2, color='red')
    # ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # ax3.xaxis.gcf().autofmt_xdate()
    ax3.fmt_xdata = mdates.DateFormatter('%Y-%m')
    ax3.set_title('Filtered P&L')
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Returns')
    plt.setp(ax3.get_xticklabels(), rotation=30, ha='right')
    ax3.grid(True)
    callback()


def plot_page(pp, page_data, iheight, iwidth, dpi, callback):
    count = len(page_data)
    fig: plt.Figure = plt.figure(figsize=(iwidth * 3 + 5, iheight * count + 5), dpi=dpi)
    axss = fig.subplots(nrows=count, ncols=3)
    for ax, data in zip(axss, page_data):
        plot_cumcurve(ax, data, callback)
    fig.tight_layout()
    fig.savefig(pp, format='pdf')
    plt.close(fig)


def plot_cumcurves(save_path, data, iheight=5, iwidth=5, dpi=32, callback=cb, maxrow=5):
    if save_path is None:
        if not os.path.exists('images'):
            os.makedirs('images')

        save_path = os.path.join('images', datetime.datetime.now().isoformat() + '.pdf')

    assert save_path.endswith('.pdf'), 'must be saved in PDF!'

    pp = PdfPages(save_path)

    # 对数据进行一个分割
    splited = [data[i:i + maxrow] for i in range(0, len(data), maxrow)]

    for page in splited:
        plot_page(pp=pp, page_data=page, iheight=iheight, iwidth=iwidth, dpi=dpi, callback=callback)

    pp.close()

    return save_path
