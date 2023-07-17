import requests
import pandas as pd


def get_market_data(ticker, interval, limit=500):

    url = f'https://api.binance.com/api/v3/klines?symbol={ticker}&' \
          f'interval={interval}&limit={limit}'
    response = requests.get(url).json()
    header = ['time', 'open', 'high', 'low', 'close', 'volume']
    candle_data = [[pd.to_datetime(candle[0], unit='ms'), float(candle[1]),
                    float(candle[2]), float(candle[3]), float(candle[4]),
                    float(candle[5])] for candle in response]
    return pd.DataFrame(candle_data, columns=header)


def get_pdh_pdl(ticker):
    url = f'https://api.binance.com/api/v3/klines?symbol={ticker}&' \
          f'interval=1d&limit={2}'
    response = requests.get(url).json()
    return float(response[0][2]), float(response[0][3])
