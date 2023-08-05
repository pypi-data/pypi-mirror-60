from .bar import Bar
from .frequency import supported, deltas
import pandas as pd
import numpy as np
import array

from multiprocessing.shared_memory import SharedMemory

import config
import os


# 通过一组 API 来统一
# 这样不怕接口变动

def bundle_valid(bundle_path):
    return os.path.exists(bundle_path)


def ls_bundle(bundle_path):
    return os.listdir(bundle_path)


def get_freq_filename(bundle, instrument, frequency):
    return os.path.join(bundle, instrument, frequency + config.bundle_ext)


def frequency_supported(bundle, instrument, frequency):
    return os.path.exists(get_freq_filename(bundle, instrument, frequency))


def read_data(bundle, instrument, frequency):
    file = get_freq_filename(bundle, instrument, frequency)
    with pd.HDFStore(file) as hdf:
        data = hdf.get(config.bundle_key)
    return data


class LocalQuotation:
    def __init__(self):

        self.loaded = False

        self.len = 0
        self.len_p = 0

        self.data = None
        self.data_p = None

        # 用于存储共享内存的信息 （防止被释放）
        self.shm = None
        self.shm_p = None

        self.bar = []
        self.bar_p = []

        self.bundle = None

    def close_share(self):
        self.shm.close()
        self.shm_p.close()

        self.shm.unlink()
        self.shm_p.unlink()

    # 将数据分享
    def share_memory(self):
        """[summary]
            通过SharedMemory在进程间分享数据。
            注意：提供者的数据并不是在SharedMemory之上建立的
        Returns:
            [type] `dict` -- [description] 我们将共享内存块的名称，大小，类型以字典的方式返回，这样可以方便其他进程加载
        """
        assert self.loaded, 'Must be loaded!'

        self.shm = SharedMemory(create=True, size=self.data.nbytes)
        temp_array = np.ndarray(shape=self.data.shape, dtype=self.data.dtype, buffer=self.shm.buf)
        temp_array[:] = self.data[:]

        self.shm_p = SharedMemory(create=True, size=self.data_p.nbytes)
        temp_array = np.ndarray(shape=self.data_p.shape, dtype=self.data_p.dtype, buffer=self.shm_p.buf)
        temp_array[:] = self.data_p[:]

        return (self.shm.name, self.data.shape), (self.shm_p.name, self.data_p.shape)

        # 从共享内存加载数据

    def load_from_shared_memory(self, name_info):

        (name, shape), (name_p, shape_p) = name_info

        self.shm = SharedMemory(name=name)
        self.data = np.ndarray(shape=shape, dtype=np.float64, buffer=self.shm.buf)

        self.shm_p = SharedMemory(name=name_p)
        self.data_p = np.ndarray(shape=shape_p, dtype=np.float64, buffer=self.shm_p.buf)

        for data in self.data:
            self.bar.append(Bar(data))
        for data_p in self.data_p:
            self.bar_p.append(Bar(data_p))

        self.loaded = True

    # 从Bundle 文件中加载数据
    def load(self, instrument, frequency, start, end, bundle, period_only=False):
        """
            加载指定的行情数据包，你可以灵活地配置。
        :param instrument:  Instrument identifier
        :param frequency:  trade frequecny , you can lookup in quotation.frequency
        :param start: data start from
        :param end:  data end to
        :param bundle:  path to data bundle, like `data/bundles/ratio`
        :param period_only: whether only load periodical data
        :return:
        """
        assert bundle_valid(bundle), f' This Bundle({bundle}) is not valid!.'
        assert instrument in ls_bundle(bundle), f'This Instrument({instrument}) is not supported by Bundle {bundle}'
        assert frequency_supported(bundle, instrument,
                                   frequency), f'This Frequency({frequency}) is not supported,bundle:{bundle},instrument{instrument}'
        self.bundle = bundle

        if not period_only:
            # 读入分钟级别数据

            self.df = read_data(bundle, instrument, config.basic_freq)
            self.df = self.df[start:end]
            if 'Volume' not in self.df.columns:
                self.df.loc[:, 'Volume'] = 0
            self.df = self.df[
                ['AskOpen', 'AskHigh', 'AskLow', 'AskClose', 'BidOpen', 'BidHigh', 'BidLow', 'BidClose', 'Volume']]

            start_time = np.asarray(self.df.index, dtype=f'datetime64[{config.basic_unit}]')
            end_time = start_time + np.timedelta64(1, f'{config.basic_unit}')
            start_time = start_time.astype(np.float64).reshape((start_time.shape[0], 1,))
            end_time = end_time.astype(np.float64).reshape((start_time.shape[0], 1,))

            bar = np.asarray(self.df)

            self.data = np.concatenate((start_time, end_time, bar), axis=1)
            for data in self.data:
                self.bar.append(Bar(data))
        # 读入低频采样的数据

        self.df_p = read_data(bundle, instrument, frequency)
        self.df_p = self.df_p[start:end]
        if 'Volume' not in self.df_p.columns:
            self.df_p.loc[:, 'Volume'] = 0

        self.df_p = self.df_p[
            ['AskOpen', 'AskHigh', 'AskLow', 'AskClose', 'BidOpen', 'BidHigh', 'BidLow', 'BidClose', 'Volume']]

        start_time_p = np.asarray(self.df_p.index, dtype='datetime64[m]')
        end_time_p = start_time_p + deltas[frequency]
        start_time_p = start_time_p.astype(np.float64).reshape((start_time_p.shape[0], 1,))
        end_time_p = end_time_p.astype(np.float64).reshape((start_time_p.shape[0], 1,))

        bar_p = np.asarray(self.df_p)

        self.data_p = np.concatenate((start_time_p, end_time_p, bar_p), axis=1)

        for data_p in self.data_p:
            self.bar_p.append(Bar(data_p))
        self.loaded = True
