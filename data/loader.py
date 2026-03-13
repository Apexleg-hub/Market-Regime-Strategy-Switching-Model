"""
data/loader.py
──────────────
MT5 data loader.

load_ohlcv()  — primary entry point.
  1. Tries to load from data/cleaned/<SYMBOL>_<TF>.pkl  (real MT5 exports)
  2. Falls back to synthetic generator so the app always works offline.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from config.constants import SYMBOL_BASE_PRICES, TF_HOURS

DATA_DIR = Path("data/cleaned")


def load_ohlcv(symbol: str, timeframe: str, n_bars: int = 500) -> pd.DataFrame:
    """Load OHLCV for symbol/timeframe from pkl or synthetic fallback."""
    pkl_path = DATA_DIR / f"{symbol}_{timeframe}.pkl"
    if pkl_path.exists():
        df = _load_pkl(pkl_path)
        return df.tail(n_bars).copy()
    return _generate_synthetic(symbol, timeframe, n_bars)


def _load_pkl(path: Path) -> pd.DataFrame:
    with open(path, "rb") as f:
        obj = pickle.load(f)
    df = pd.DataFrame(obj) if isinstance(obj, dict) else obj.copy()
    df.columns = [c.lower() for c in df.columns]
    required = {"open", "high", "low", "close", "volume"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"PKL missing columns: {missing}")
    if not isinstance(df.index, pd.DatetimeIndex):
        for col in ("time", "date", "datetime", "timestamp"):
            if col in df.columns:
                df.index = pd.to_datetime(df[col])
                df.drop(columns=[col], inplace=True)
                break
    df.sort_index(inplace=True)
    return df


def _generate_synthetic(symbol: str, timeframe: str, n_bars: int) -> pd.DataFrame:
    """Deterministic synthetic OHLCV cycling through all five regimes."""
    seed = 42 + hash(symbol + timeframe) % 999
    rng  = np.random.default_rng(seed)

    regime_schedule = [
        ("bull", 80), ("high_vol", 40), ("ranging", 60),
        ("bear", 70), ("low_vol",  50), ("ranging", 80),
        ("bull", 90), ("high_vol", 35), ("bear",    50),
        ("low_vol", 45),
    ]
    regimes_full: list[str] = []
    for r, length in regime_schedule:
        regimes_full.extend([r] * length)
    regimes_full = (regimes_full * 4)[:n_bars]

    price = SYMBOL_BASE_PRICES.get(symbol, 1.0)
    prices = [price]
    _params = {
        "bull":     ( 0.0003,  0.0006),
        "bear":     (-0.0003,  0.0006),
        "high_vol": ( 0.0001,  0.0020),
        "low_vol":  ( 0.00005, 0.0002),
        "ranging":  ( 0.0,     0.0007),
    }
    for i in range(1, n_bars):
        mu, sigma = _params[regimes_full[i]]
        prices.append(prices[-1] * (1 + rng.normal(mu, sigma)))

    prices = np.array(prices)
    highs  = prices * (1 + np.abs(rng.normal(0, 0.0004, n_bars)))
    lows   = prices * (1 - np.abs(rng.normal(0, 0.0004, n_bars)))
    vols   = rng.integers(800, 4000, n_bars).astype(float)

    freq_min = max(1, int(TF_HOURS.get(timeframe, 4.0) * 60))
    idx = pd.date_range(end=pd.Timestamp("2024-12-31"), periods=n_bars,
                        freq=f"{freq_min}min")
    return pd.DataFrame(
        {"open": prices, "high": highs, "low": lows,
         "close": prices, "volume": vols},
        index=idx,
    )
