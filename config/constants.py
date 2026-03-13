"""
config/constants.py
───────────────────
All project-wide constants: regime definitions, feature columns,
available symbols/timeframes, and Plotly theme settings.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


# ─── REGIME DEFINITIONS ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class RegimeInfo:
    label:      str
    css_class:  str
    color:      str
    icon:       str
    strategy:   str
    description: str


REGIMES: Dict[int, RegimeInfo] = {
    0: RegimeInfo(
        label="Bull Trend",
        css_class="bull",
        color="#00d97e",
        icon="▲",
        strategy="Moving Average / Momentum",
        description="Ride the trend. MA crossover entries, trailing stops.",
    ),
    1: RegimeInfo(
        label="Bear Trend",
        css_class="bear",
        color="#ff4d6d",
        icon="▼",
        strategy="Inverse Momentum / Short MA",
        description="Fade rallies. Short bias with MA confirmation.",
    ),
    2: RegimeInfo(
        label="High Volatility",
        css_class="high",
        color="#f59e0b",
        icon="⚡",
        strategy="Breakout / Vol Expansion",
        description="Trade breakouts from key levels. ATR-scaled position sizing.",
    ),
    3: RegimeInfo(
        label="Low Volatility",
        css_class="low",
        color="#38bdf8",
        icon="◈",
        strategy="Carry Trade / Range Scalp",
        description="Sell premium. Tight range scalping. Low position sizing.",
    ),
    4: RegimeInfo(
        label="Range Market",
        css_class="range",
        color="#a78bfa",
        icon="↔",
        strategy="Mean Reversion / Oscillator",
        description="Buy support, sell resistance. RSI/Bollinger reversion.",
    ),
}

REGIME_COLORS: Dict[int, str] = {rid: r.color for rid, r in REGIMES.items()}


# ─── FEATURE COLUMNS ──────────────────────────────────────────────────────────

FEATURE_COLS = [
    "ret_1",
    "vol_5",
    "vol_20",
    "trend_strength",
    "ma_slope",
    "rsi_14",
    "bb_width",
    "roc_10",
]


# ─── MT5 DATA SETTINGS ────────────────────────────────────────────────────────

SYMBOLS     = ["EURUSD", "GBPUSD", "USDJPY"]
TIMEFRAMES  = ["H4", "D1", "WK", "H1"]

SYMBOL_BASE_PRICES: Dict[str, float] = {
    "EURUSD": 1.0850,
    "GBPUSD": 1.2650,
    "USDJPY": 148.50,
}

TF_HOURS: Dict[str, float] = {
    "M1":  1 / 60,
    "M5":  5 / 60,
    "H1":  1.0,
    "H4":  4.0,
    "D1":  24.0,
    "WK":  168.0,
    "MN":  720.0,
}


# ─── ALGORITHM OPTIONS ────────────────────────────────────────────────────────

MODEL_OPTIONS = [
    "Hidden Markov Model (HMM)",
    "Gaussian Mixture Model (GMM)",
    "K-Means Clustering",
]


# ─── PLOTLY DARK THEME ────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0a0e1a",
    plot_bgcolor="#0a0e1a",
    font=dict(family="JetBrains Mono, monospace", color="#64748b", size=11),
    xaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e2a3a", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="#111827", bordercolor="#1e2a3a", borderwidth=1),
)

PALETTE = ["#00d97e", "#ff4d6d", "#f59e0b", "#38bdf8", "#a78bfa"]
