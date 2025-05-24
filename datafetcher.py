# datafetcher.py
import pandas as pd
import logging
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

def fetch_data(symbol, timeframe):
    try:
        candles = client.get_klines(symbol=symbol, interval=timeframe, limit=100)
        if not candles or len(candles[0]) != 12:
            logging.error(f"Unexpected data structure for {symbol} on {timeframe}: {candles}")
            return None

        df = pd.DataFrame(candles, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)
        return df
    except Exception as e:
        logging.error(f"Error fetching data for {symbol} on {timeframe}: {e}", exc_info=True)
        return None
