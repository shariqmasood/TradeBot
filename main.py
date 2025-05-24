# main.py

# Optional monkey patches for Python 3.13 + pandas_ta + NumPy
import pkgutil
if not hasattr(pkgutil, 'ImpImporter'):
    pkgutil.ImpImporter = pkgutil.zipimporter

import numpy as np
if not hasattr(np, 'NaN'):
    np.NaN = np.nan

import time
import logging
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed

from datafetcher import fetch_data
from indicators import calculate_indicators
from conditions import grade_long_opportunity, is_btc_bullish
from utils import calculate_long_tp_sl
from simulation import SimulationAccount
from config import TIMEFRAMES, SLEEP_INTERVAL, LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),
        logging.StreamHandler()
    ]
)

# Create a simulation account with an initial balance of 1000 USDT.
sim_account = SimulationAccount(initial_balance=1000.0)
# Manually chosen altcoins for tracking
coins_to_track = ["ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT"]

shutdown_flag = False
def signal_handler(signum, frame):
    global shutdown_flag
    logging.info("Received termination signal. Shutting down gracefully...")
    shutdown_flag = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Fetch BTC data once at startup (and at every cycle) to get BTC bullish score.
logging.info("Fetching BTC data to determine bullishness...")
btc_df = fetch_data("BTCUSDT", TIMEFRAMES["execution"])
if btc_df is not None:
    btc_df = calculate_indicators(btc_df)
btc_bullish_score = is_btc_bullish(btc_df) if btc_df is not None else 0
logging.info(f"BTC Bullish Score: {btc_bullish_score}")

def process_coin(coin, btc_bullish_score):
    try:
        logging.info(f"Fetching data for {coin}...")
        df_3m = fetch_data(coin, TIMEFRAMES["execution"])
        if df_3m is None:
            logging.warning(f"No data for {coin} on {TIMEFRAMES['execution']}")
            return

        df_3m = calculate_indicators(df_3m)
        if df_3m is None or df_3m.empty:
            logging.warning(f"Indicators not calculated for {coin}")
            return

        latest = df_3m.iloc[-1]
        entry_price = latest["close"]
        atr = latest["ATR"]

        # For long opportunities we use a 14-period RSI
        rsi_14 = latest.get("RSI", 0)
        ema7 = latest.get("EMA_7", 0)
        ema21 = latest.get("EMA_21", 0)
        macd = latest.get("MACD", 0)
        volume_spike = latest.get("Volume_Spike", 0)
        stoch_rsi_k = latest.get("StochRSI_k", 0)

        # Include BTC bullish score into the grading
        grade, score = grade_long_opportunity(
            rsi_14, ema7, ema21, macd, volume_spike, stoch_rsi_k, btc_bullish_score
        )
        logging.info(f"{coin} Long Opportunity Grade: {grade} (score: {score})")

        if grade == "Long Opportunity" and coin not in sim_account.open_trades:
            tp, sl = calculate_long_tp_sl(coin, entry_price, atr)
            sim_account.enter_trade(coin, entry_price, tp, sl, trade_type="long", allocation=0.1, atr=atr)

        sim_account.update_trades(coin, entry_price)
    except Exception as e:
        logging.error(f"Error processing {coin}: {e}", exc_info=True)

def monitor_coins():
    # Refresh BTC bullish score on each cycle.
    logging.info("Fetching BTC data to determine bullishness...")
    btc_df = fetch_data("BTCUSDT", TIMEFRAMES["execution"])
    if btc_df is not None:
        btc_df = calculate_indicators(btc_df)
    btc_score = is_btc_bullish(btc_df) if btc_df is not None else 0
    logging.info(f"BTC Bullish Score: {btc_score}")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_coin, coin, btc_score): coin for coin in coins_to_track}
        for future in as_completed(futures):
            coin = futures[future]
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread processing {coin}: {e}", exc_info=True)

if __name__ == "__main__":
    while not shutdown_flag:
        logging.info("Starting coin monitoring cycle...")
        monitor_coins()
        logging.info("Cycle complete. Sleeping for 3 minutes...")
        time.sleep(SLEEP_INTERVAL)
    sim_account.summary()
