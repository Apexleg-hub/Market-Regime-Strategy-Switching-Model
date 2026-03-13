"""
utils/pipeline.py
=================
Orchestration helper — runs the full pipeline end-to-end and caches results
in Streamlit session_state.

Wires together:
    data.loader  →  features.engineer  →  models.get_detector
    →  strategy.signals  →  backtest.engine
"""

from __future__ import annotations

import streamlit as st

from data.loader      import load_symbol
from features.engineer import engineer_features
from models           import get_detector
from strategy.signals  import generate_signals
from backtest.engine   import run_backtest
from backtest.engine   import BacktestResult
from models.base       import RegimeResult


SESSION_KEY = "regime_results"


def run_pipeline(
    symbol:       str,
    timeframe:    str,
    n_bars:       int,
    model_type:   str,
    n_states:     int,
    slippage_bps: int,
) -> dict:
    """
    Execute the full regime-switching pipeline and cache the result.

    Returns a flat dict with all artefacts needed by the UI layer.
    """
    # ── 1. Load market data ──────────────────────────────────────────────────
    df_raw = load_symbol(symbol, timeframe, n_bars)

    # ── 2. Feature engineering ───────────────────────────────────────────────
    df = engineer_features(df_raw.copy())

    # ── 3. Regime detection ──────────────────────────────────────────────────
    detector: "BaseRegimeDetector" = get_detector(model_type, n_states=n_states)
    result:   RegimeResult         = detector.detect(df)

    # ── 4. Strategy signals ──────────────────────────────────────────────────
    signals = generate_signals(df, result.regime_series)

    # ── 5. Backtest ──────────────────────────────────────────────────────────
    bt: BacktestResult = run_backtest(df, signals, slippage=slippage_bps / 10_000)

    return {
        "df":            df,
        "regime_series": result.regime_series,
        "regime_ids":    result.regime_ids,
        "probs":         result.probs,
        "signals":       signals,
        "equity":        bt.equity,
        "buy_and_hold":  bt.buy_and_hold,
        "strat_ret":     bt.returns,
        "metrics":       bt.metrics,
    }


def get_or_run(
    symbol:       str,
    timeframe:    str,
    n_bars:       int,
    model_type:   str,
    n_states:     int,
    slippage_bps: int,
    force_rerun:  bool = False,
) -> dict:
    """
    Return cached results from session_state, or run the pipeline fresh.

    Parameters
    ----------
    force_rerun : set True when the user clicks 'Run Model'.
    """
    if SESSION_KEY not in st.session_state or force_rerun:
        with st.spinner("Loading data & fitting regime model…"):
            st.session_state[SESSION_KEY] = run_pipeline(
                symbol, timeframe, n_bars, model_type, n_states, slippage_bps
            )
    return st.session_state[SESSION_KEY]
