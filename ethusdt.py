from binance import Client
import time
import numpy as np

client = Client(api_key='your_api_key', api_secret='your_api_secret')

eth_list = []
btc_list = []
free_eth = []

while True:
    eth_usd_futures = client.futures_recent_trades(symbol='ETHUSDT')
    btc_usd_futures = client.futures_recent_trades(symbol='BTCUSDT')
    eth_usd_futures_price = float(eth_usd_futures[-1]['price'])
    btc_usd_futures_price = float(btc_usd_futures[-1]['price'])
    print(eth_usd_futures_price)
    eth_list.append(eth_usd_futures_price)
    btc_list.append(btc_usd_futures_price)

    if len(eth_list) > 10:
        corr_matrix = np.corrcoef(eth_list[-10:], btc_list[-10:])
        correlation = corr_matrix[0, 1]

        print(f'Correlation between ETHUSD and BTCUSDT: {correlation}')

        if correlation < 0.5:
            print(f'Correlation is small: {correlation}')
            free_eth.append(eth_usd_futures_price)
            print(f'Adding ETHUSD price to list:{eth_usd_futures_price}')
            time.sleep(1)
        else:
            time.sleep(0.5)
    if len(free_eth) > 5:
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

    else:
        time.sleep(0.5)