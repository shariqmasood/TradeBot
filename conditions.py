# conditions.py
import logging

def is_btc_bullish(btc_df):
    """
    Evaluate BTC's bullish conditions for long trading.
    For example, if:
      - RSI (14) > 50,
      - EMA(7) > EMA(21),
      - MACD > 0,
    then return 3 points; otherwise 0.
    """
    try:
        latest = btc_df.iloc[-1]
        rsi = latest.get("RSI", 0)
        ema7 = latest.get("EMA_7", 0)
        ema21 = latest.get("EMA_21", 0)
        macd = latest.get("MACD", 0)
        if rsi > 50 and ema7 > ema21 and macd > 0:
            return 3
        return 0
    except Exception as e:
        logging.error(f"Error checking BTC bullishness: {e}", exc_info=True)
        return 0

def grade_long_opportunity(rsi_14, ema7, ema21, macd, volume_spike, stoch_rsi_k, btc_bullish_score):
    """
    Grades a potential long (spot) opportunity using altcoin signals plus BTC bullish scoring.
    Criteria (example weights):
      - RSI(14) < 40 → +3 points
      - EMA(7) > EMA(21) → +2 points
      - MACD > 0 → +2 points
      - Volume Spike > 1.5 → +2 points
      - StochRSI (K) < 20 → +1 point
    Then add the BTC bullish score.
    If the total score is at least LONG_SCORE_THRESHOLD (e.g., 7), return "Long Opportunity"; otherwise, "Neutral".
    """
    score = 0
    if rsi_14 < 40:
        score += 3
    if ema7 > ema21:
        score += 2
    if macd > 0:
        score += 2
    if volume_spike > 1.5:
        score += 2
    if stoch_rsi_k < 20:
        score += 1

    score += btc_bullish_score

    LONG_SCORE_THRESHOLD = 7
    if score >= LONG_SCORE_THRESHOLD:
        return "Long Opportunity", score
    return "Neutral", score
