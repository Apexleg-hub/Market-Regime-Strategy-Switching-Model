"""
ui/tabs.py
──────────
One render function per tab.  Each is called from app.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from backtest.engine  import BacktestResult
from config.constants import REGIMES, FEATURE_COLS
from ui.components    import section_header
from ui import charts


# ─── TAB 1 ───────────────────────────────────────────────────────────────────

def render_price_tab(
    df: pd.DataFrame,
    regime_ids: np.ndarray,
    symbol: str,
    timeframe: str,
    model_short: str,
) -> None:
    section_header("PRICE CHART WITH DETECTED REGIMES")
    fig = charts.price_regime_chart(df, regime_ids, symbol, timeframe, model_short)
    st.plotly_chart(fig, use_container_width=True)


# ─── TAB 2 ───────────────────────────────────────────────────────────────────

def render_probability_tab(
    df: pd.DataFrame,
    regime_ids: np.ndarray,
    probs: np.ndarray,
) -> None:
    section_header("STATE PROBABILITY HEATMAP")
    st.plotly_chart(charts.state_probability_chart(df, probs), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section_header("REGIME TRANSITION MATRIX")
        st.plotly_chart(charts.transition_matrix_chart(regime_ids), use_container_width=True)
    with col_b:
        section_header("REGIME DURATION (BARS)")
        st.plotly_chart(charts.regime_duration_chart(regime_ids), use_container_width=True)


# ─── TAB 3 ───────────────────────────────────────────────────────────────────

def render_equity_tab(
    df: pd.DataFrame,
    result: BacktestResult,
    regime_series: pd.Series,
) -> None:
    section_header("STRATEGY EQUITY CURVE")
    st.plotly_chart(
        charts.equity_curve_chart(df, result.equity, result.benchmark),
        use_container_width=True,
    )

    col_dd, col_ret = st.columns(2)
    with col_dd:
        section_header("DRAWDOWN")
        st.plotly_chart(charts.drawdown_chart(df, result.equity), use_container_width=True)
    with col_ret:
        section_header("RETURN DISTRIBUTION")
        st.plotly_chart(charts.return_distribution_chart(result.returns), use_container_width=True)

    section_header("PERFORMANCE BY REGIME", margin_top="16px")
    st.dataframe(_per_regime_table(result, regime_series), use_container_width=True, hide_index=True)


def _per_regime_table(result: BacktestResult, regime_series: pd.Series) -> pd.DataFrame:
    rows = []
    for rid, r in REGIMES.items():
        mask   = regime_series.shift(1).ffill() == rid
        r_rets = result.returns[mask]
        if len(r_rets) == 0:
            continue
        total_r  = (1 + r_rets).prod() - 1
        sharpe_r = r_rets.mean() / (r_rets.std() + 1e-10) * (252 ** 0.5)
        win_rate = (r_rets > 0).mean()
        rows.append({
            "Regime":       f"{r.icon} {r.label}",
            "Bars":         int(mask.sum()),
            "Total Return": f"{total_r * 100:+.2f}%",
            "Sharpe":       f"{sharpe_r:.2f}",
            "Win Rate":     f"{win_rate * 100:.1f}%",
        })
    return pd.DataFrame(rows)


# ─── TAB 4 ───────────────────────────────────────────────────────────────────

def render_features_tab(df: pd.DataFrame) -> None:
    section_header("FEATURE ENGINEERING OUTPUT")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.plotly_chart(charts.volatility_chart(df), use_container_width=True)
    with col_f2:
        st.plotly_chart(charts.rsi_chart(df), use_container_width=True)
    with col_f1:
        st.plotly_chart(charts.trend_strength_chart(df), use_container_width=True)
    with col_f2:
        st.plotly_chart(charts.bb_width_chart(df), use_container_width=True)

    section_header("FEATURE CORRELATION MATRIX", margin_top="16px")
    st.plotly_chart(charts.correlation_heatmap(df, FEATURE_COLS), use_container_width=True)
