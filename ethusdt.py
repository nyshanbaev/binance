from binance import Client
import time
import numpy as np
import pandas as pd
import requests


ETHUSDT = 'https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=1s&limit=5'
BTCUSDT = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1s&limit=5'

client = Client(api_key='your_api_key', api_secret='your_api_secret')

free_eth = []
start_time = time.time()

while True:

    current_time = time.time()
    eth_usd_futures = client.futures_recent_trades(symbol='ETHUSDT')
    eth_usd_futures_price = float(eth_usd_futures[-1]['price'])
    print(eth_usd_futures_price)

    def parse_data(url):
        data = requests.get(url).json()
        df = pd.DataFrame(data)
        df = df.iloc[:,:6]
        col_names = ['time', 'open', 'high', 'low', 'close', 'volume']
        df.columns = col_names
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df.set_index('time', inplace=True)
        for col in df.columns:
            df[col] = df[col].astype(float)
        return df

    eth_df = parse_data(ETHUSDT)
    btc_df = parse_data(BTCUSDT)

    corr_matrix = np.corrcoef(eth_df['close'], btc_df['close'])
    corr = corr_matrix[0,1]

    print(f"Correlation between ETHUSDT and BTCUSDT: {corr}")

    if corr < 0.2 and corr > -0.2:
        free_eth.append(eth_usd_futures_price)
    
    if current_time - start_time >= 3600:
        prev_price = free_eth[0]

        for price in free_eth[1:]:
            percent_change = abs(price - prev_price) / prev_price * 100
            if percent_change >= 1:
                print(f"ETH changed by {percent_change}%")
            prev_price = price

        n = 14
        tr_list = []
        for i in range(1, len(free_eth)):
            high = free_eth[i]
            low = free_eth[i]
            if i == 1:
                prev_close = free_eth[0]
            else:
                prev_close = free_eth[i-1]
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)

        atr = sum(tr_list[-n:]) / n
        print(f"ATR: {atr}")
        free_eth.clear()
        tr_list.clear()
        start_time = current_time

    time.sleep(5)
