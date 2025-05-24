# utils.py
import logging
from fib import calculate_fib_levels  # Optional, if you wish to integrate Fibonacci retracement later

def calculate_short_tp_sl(symbol, entry_price, atr, swing_low=None, swing_high=None):
    tp_multiplier = 3.0
    sl_multiplier = 1.5
    tp = entry_price - atr * tp_multiplier
    sl = entry_price + atr * sl_multiplier
    return tp, sl

def calculate_long_tp_sl(symbol, entry_price, atr, swing_low=None, swing_high=None):
    tp_multiplier = 3.0  # target profit multiplier
    sl_multiplier = 1.5  # stop loss multiplier
    tp = entry_price + atr * tp_multiplier
    sl = entry_price - atr * sl_multiplier
    return tp, sl
