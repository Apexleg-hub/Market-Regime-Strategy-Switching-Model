"""
strategy/signals.py
───────────────────
Regime-adaptive signal generator.

Each regime has a dedicated signal function.  The dispatcher
generate_signals() routes each bar to the correct sub-strategy
based on the detected regime label.

Signal convention
-----------------
 +1  Long
  0  Flat
 -1  Short
"""

from __future__ import annotations

import numpy as np
import pandas as pd


# ─── SUB-STRATEGY LOGIC ───────────────────────────────────────────────────────

def _bull_trend_signal(row: pd.Series) -> int:
    """MA crossover — long when fast > slow."""
    return 1 if row["ma_20"] > row["ma_50"] else 0


def _bear_trend_signal(row: pd.Series) -> int:
    """Inverse MA — short when fast < slow."""
    return -1 if row["ma_20"] < row["ma_50"] else 0


def _high_vol_signal(row: pd.Series) -> int:
    """Breakout — enter in direction of a 1-bar return exceeding 1-std."""
    if row["ret_1"] >  row["vol_5"]:
        return  1
    if row["ret_1"] < -row["vol_5"]:
        return -1
    return 0


def _low_vol_signal(row: pd.Series) -> int:
    """Carry / range scalp — flat long bias."""
    return 1


def _ranging_signal(row: pd.Series) -> int:
    """Mean reversion — fade overbought/oversold RSI."""
    if row["rsi_14"] > 65:
        return -1
    if row["rsi_14"] < 35:
        return  1
    return 0


# ─── DISPATCHER ───────────────────────────────────────────────────────────────

_STRATEGY_MAP = {
    0: _bull_trend_signal,
    1: _bear_trend_signal,
    2: _high_vol_signal,
    3: _low_vol_signal,
    4: _ranging_signal,
}


def generate_signals(df: pd.DataFrame, regime_series: pd.Series) -> pd.Series:
    """
    Produce a signal series aligned with *df*.

    Parameters
    ----------
    df             : feature-engineered OHLCV DataFrame
    regime_series  : integer regime IDs (0-4) aligned with df

    Returns
    -------
    pd.Series of int {-1, 0, 1}
    """
    signals = pd.Series(0, index=df.index, dtype=int)

    for i in range(1, len(df)):
        regime   = int(regime_series.iloc[i])
        strategy = _STRATEGY_MAP.get(regime, lambda r: 0)
        signals.iloc[i] = strategy(df.iloc[i])

    return signals
