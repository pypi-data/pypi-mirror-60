from runner import BackTestRunner, Context
from multiprocessing import Process, Manager
from quotation import LocalQuotation

import traceback
import os
import queue


def work(str_module_name, commission_rate, frequency, shm_names, p, q):
    str_module = __import__(str_module_name)

    qt = LocalQuotation()
    qt.load_from_shared_memory(shm_names)

    temp_ctx = Context()
    temp_ctx.quotation = qt
    temp_ctx.commission_rate = commission_rate
    temp_ctx.frequency = frequency

    while True:
        try:
            param = p.get_nowait()
            temp_ctx.parameters_instance = param
            temp_ctx.instrument = param["instrument"]
            temp_ctx.initial_cash = param['initial_cash']
            bt = BackTestRunner(str_module, temp_ctx)
            bt.run()
            bt.conclude()

            q.put((param, bt.cost_functions))
        except queue.Empty as e:
            return
        except Exception as e:
            traceback.print_exc()


def run_scan(str_module_name, ctx, params, process_count=None):
    results = []
    processes = []
    manager = Manager()

    q = manager.Queue()
    p = manager.Queue()

    if process_count is None:
        process_count = os.cpu_count()

    try:

        quotation_shm_name = ctx.quotation.share_memory()

        # 发送参数
        for param in params:
            p.put(param)

        for i in range(process_count):
            processes.append(Process(group=None, name=f'newtrade_scanner_{i}', target=work,
                                     args=(str_module_name, ctx.commission_rate,
                                           ctx.frequency, quotation_shm_name, p, q)))

        for process in processes:
            process.start()

        from tqdm import tqdm
        t = tqdm(total=len(params), unit='task', smoothing=False)
        t.update(0)
        for i in range(len(params)):
            params, cost_functions = q.get(timeout=None)
            results.append(dict(params, **cost_functions))
            t.update()
        t.close()

        # 等待结束
        for process in processes:
            process.join(timeout=None)

    except Exception as e:
        t.close()
        traceback.print_exc()

    return results
