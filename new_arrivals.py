import websocket
import json
from datetime import datetime
import requests
import time
import multiprocessing


EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"
KLINE_URL = "https://api.binance.com/api/v3/klines"

KLINE_INTERVAL = "1d"
KLINE_LIMIT = 1000

manager = multiprocessing.Manager()
shared_list = manager.list()

def main():
    exchange_info = get_exchange_info()
    pairs = get_pairs(exchange_info)
    busd_pairs = filter_busd_pairs(pairs)
    for bp in busd_pairs:
        p = multiprocessing.Process(target=init_ops, args=(shared_list, bp,))
        p.start()
    time.sleep(5)

    sorted_list = sorted(shared_list, key=lambda i: i['fs_ratio'])
    for _, i in enumerate(sorted_list[:]):
        print(i)



def init_ops(sorted_list, pair):  
    klines = get_kline(pair, KLINE_INTERVAL, KLINE_LIMIT)
    if 10 > len(klines):
        print(pair)
    
    # sorted_list.append({"symbol": pair, "fall_short": fall_short, "length": len(klines), "fs_ratio": (fall_short * 100) / len(klines)})


def get_ohlc(klines):
    open = [float(o[1]) for o in klines]
    high = [float(h[2]) for h in klines]
    low = [float(l[3]) for l in klines]
    close = [float(c[4]) for c in klines]
    return open, high, low, close



def get_kline(kline_symbol, kline_interval, kline_limit):
    try:
        params = {"symbol": kline_symbol, "interval": kline_interval, "limit": kline_limit}
        response = requests.get(
            url=f"{KLINE_URL}", params=params)
        response.raise_for_status()
        kline = response.json()
        # kline = kline[:-1]
        return kline
    except requests.exceptions.RequestException as err:
        print(err)
        return None


def filter_busd_pairs(pairs):
    busd_paris = []
    for pair in pairs:
        if "BUSD" in pair or "USDT" in pair:
            busd_paris.append(pair)
    return busd_paris


def get_pairs(exchange_info):
    pairs = []
    for symbol in exchange_info["symbols"]:
        pairs.append(symbol["symbol"])
    return pairs


def get_exchange_info():
    response = requests.get(EXCHANGE_INFO)
    exchange_info = response.json()
    return exchange_info


if __name__ == "__main__":
    main()