# indicators.py
import pandas_ta as ta
import logging

def calculate_indicators(df):
    try:
        if len(df) < 21:
            logging.warning("Insufficient data for calculating indicators.")
            return df

        df["EMA_7"] = ta.ema(df["close"], length=7)
        df["EMA_9"] = ta.ema(df["close"], length=9)
        df["EMA_21"] = ta.ema(df["close"], length=21)
        df["RSI"] = ta.rsi(df["close"], length=14)
        df["RSI_12"] = ta.rsi(df["close"], length=12)
        macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
        df["MACD"] = macd["MACD_12_26_9"]
        df["MACD_signal"] = macd["MACDs_12_26_9"]
        df["SAR"] = ta.psar(df["high"], df["low"], df["close"])["PSARl_0.02_0.2"]
        adx = ta.adx(df["high"], df["low"], df["close"], length=14)
        df["ADX"] = adx["ADX_14"]
        bb = ta.bbands(df["close"], length=20)
        df["BB_upper"] = bb["BBU_20_2.0"]
        df["BB_middle"] = bb["BBM_20_2.0"]
        df["BB_lower"] = bb["BBL_20_2.0"]
        df["ATR"] = ta.atr(df["high"], df["low"], df["close"], length=14)
        if "ATR" in df.columns:
            logging.info("ATR successfully calculated.")
        else:
            raise ValueError("ATR calculation failed.")
        df["Volume_MA"] = df["volume"].rolling(window=20).mean()
        df["Volume_Spike"] = df["volume"] / df["Volume_MA"]
        rsi_min = df["RSI"].rolling(window=14).min()
        rsi_max = df["RSI"].rolling(window=14).max()
        df["StochRSI_k"] = 100 * (df["RSI"] - rsi_min) / (rsi_max - rsi_min)
        df["StochRSI_d"] = df["StochRSI_k"].rolling(window=3).mean()
        df["CCI"] = ta.cci(df["high"], df["low"], df["close"], length=20)
        ichimoku = ta.ichimoku(df["high"], df["low"], df["close"])
        if isinstance(ichimoku, tuple):
            ichimoku_df = ichimoku[0]
        else:
            ichimoku_df = ichimoku
        df["tenkan_sen"] = ichimoku_df["ISA_9"]
        df["kijun_sen"] = ichimoku_df["ISB_26"]
        df["senkou_span_a"] = (df["tenkan_sen"] + df["kijun_sen"]) / 2
        df["senkou_span_b"] = (df["high"].rolling(window=52).max() + df["low"].rolling(window=52).min()) / 2
        return df
    except Exception as e:
        logging.error(f"Error calculating indicators: {e}", exc_info=True)
        return df
