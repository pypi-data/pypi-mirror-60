import numpy as np

supported = ['5min', '15min', '30min', '1h', '4h', '6h', '1D', '1W', '1M', '5D']

deltas = {

}

for s in supported:
    if s.endswith('min'):
        deltas[s] = np.timedelta64(int(s[:-3]), 'm')
    else:
        deltas[s] = np.timedelta64(int(s[: -1]), s[-1])
