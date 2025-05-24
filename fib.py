# fib.py
def calculate_fib_levels(swing_low, swing_high):
    diff = swing_high - swing_low
    return {
        "0.0%": swing_high,
        "23.6%": swing_high - 0.236 * diff,
        "38.2%": swing_high - 0.382 * diff,
        "50.0%": swing_high - 0.5 * diff,
        "61.8%": swing_high - 0.618 * diff,
        "100.0%": swing_low
    }
