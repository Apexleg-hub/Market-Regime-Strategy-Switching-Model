"""
features/engineer.py
────────────────────
Stateless feature engineering pipeline.

engineer_features(df) takes a raw OHLCV DataFrame and returns the same
DataFrame enriched with all indicator columns needed by the regime models.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicator columns in-place and drop leading NaN rows.

    Input  : OHLCV DataFrame (columns: open, high, low, close, volume)
    Output : Same DataFrame with indicator columns appended, NaNs dropped.
    """
    df = df.copy()
    c  = df["close"]

    # ── Returns ──────────────────────────────────────────────────────────────
    df["ret_1"]  = c.pct_change(1)
    df["ret_5"]  = c.pct_change(5)
    df["ret_20"] = c.pct_change(20)

    # ── Rolling Volatility ───────────────────────────────────────────────────
    df["vol_5"]  = df["ret_1"].rolling(5).std()
    df["vol_20"] = df["ret_1"].rolling(20).std()
    df["vol_60"] = df["ret_1"].rolling(60).std()

    # ── ATR proxy ────────────────────────────────────────────────────────────
    df["atr_14"] = (df["high"] - df["low"]).rolling(14).mean()

    # ── Trend / MA ───────────────────────────────────────────────────────────
    df["ma_20"]  = c.rolling(20).mean()
    df["ma_50"]  = c.rolling(50).mean()
    df["ma_200"] = c.rolling(200).mean()

    df["trend_strength"] = (c - df["ma_50"]) / df["ma_50"]
    df["ma_slope"]       = df["ma_20"].diff(5) / df["ma_20"].shift(5)

    # ── Momentum ─────────────────────────────────────────────────────────────
    df["roc_10"] = c.pct_change(10)
    df["roc_20"] = c.pct_change(20)

    # ── RSI (14) ─────────────────────────────────────────────────────────────
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["rsi_14"] = 100 - 100 / (1 + gain / (loss + 1e-10))

    # ── Bollinger Band Width ──────────────────────────────────────────────────
    bb_std        = c.rolling(20).std()
    df["bb_width"] = (4 * bb_std) / df["ma_20"]

    # ── Volume Ratio ─────────────────────────────────────────────────────────
    df["vol_ratio"] = df["volume"] / df["volume"].rolling(20).mean()

    df.dropna(inplace=True)
    return df
