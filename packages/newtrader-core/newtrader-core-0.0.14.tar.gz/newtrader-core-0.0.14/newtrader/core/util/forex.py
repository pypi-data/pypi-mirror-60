point_rate = {}

forex_instruments = [
    'AUD/CAD', 'AUD/CHF', 'AUD/JPY', 'AUD/NZD', 'CAD/CHF', 'EUR/AUD',
    'EUR/CHF', 'EUR/GBP', 'EUR/JPY', 'EUR/USD', 'GBP/CHF', 'GBP/JPY',
    'GBP/NZD', 'GBP/USD', 'NZD/CAD', 'NZD/CHF', 'NZD/JPY', 'NZD/USD',
    'USD/CAD', 'USD/CHF', 'USD/JPY'
]

for i in forex_instruments:
    if i.endswith('JPY'):
        point_rate[i] = 100
        point_rate[i.replace('/', '')] = 100
    else:
        point_rate[i] = 10000
        point_rate[i.replace('/', '')] = 10000


def is_supported(instrument: str) -> bool:
    """
        确认标的品种是否被支持.
    :param instrument:
    :return: 是否被支持
    """
    return instrument in point_rate
