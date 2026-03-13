

"""
ui/charts.py
────────────
All Plotly figure builders.  Each function returns a go.Figure.
The calling tab renders it with st.plotly_chart().
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.constants import PLOTLY_LAYOUT, REGIME_COLORS, REGIMES, PALETTE


# ─── COLOR HELPER ────────────────────────────────────────────────────────────
# Plotly does NOT accept 8-digit hex (#rrggbbaa).
# Always use rgba() for colors that need transparency.

def _rgba(hex_color: str, alpha: float) -> str:
    """Convert a 6-digit hex string + alpha float → 'rgba(r,g,b,a)' for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ─── TAB 1 : PRICE + REGIMES ─────────────────────────────────────────────────

def price_regime_chart(
    df: pd.DataFrame,
    regime_ids: np.ndarray,
    symbol: str,
    timeframe: str,
    model_short: str,
) -> go.Figure:
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.20],
        vertical_spacing=0.04,
        subplot_titles=["Close Price + Regime Overlay", "Regime ID", "Volume"],
    )

    # Price + MAs
    fig.add_trace(go.Scatter(x=df.index, y=df["close"], mode="lines",
                              line=dict(color="#6366f1", width=1.5), name="Close"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ma_20"], mode="lines",
                              line=dict(color="#00d97e", width=1, dash="dot"), name="MA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["ma_50"], mode="lines",
                              line=dict(color="#f59e0b", width=1, dash="dot"), name="MA50"), row=1, col=1)

    # Regime background shading — opacity handled by add_vrect's own opacity param
    prev_r = None; start_i = None
    for idx_v, rv in zip(df.index, regime_ids):
        if rv != prev_r:
            if prev_r is not None:
                fig.add_vrect(x0=start_i, x1=idx_v,
                              fillcolor=REGIME_COLORS[prev_r],
                              opacity=0.08, line_width=0, row=1, col=1)
            start_i = idx_v; prev_r = rv
    if prev_r is not None:
        fig.add_vrect(x0=start_i, x1=df.index[-1],
                      fillcolor=REGIME_COLORS[prev_r],
                      opacity=0.08, line_width=0, row=1, col=1)

    # Regime ID bar
    fig.add_trace(go.Bar(
        x=df.index, y=regime_ids + 0.5,
        marker_color=[REGIME_COLORS[r] for r in regime_ids],
        name="Regime", showlegend=False, opacity=0.9,
    ), row=2, col=1)

    # Volume
    fig.add_trace(go.Bar(x=df.index, y=df["volume"],
                          marker_color="#1e2a3a", name="Volume", showlegend=False), row=3, col=1)

    fig.update_yaxes(row=2, col=1, tickvals=[0, 1, 2, 3, 4],
                     ticktext=["Bull", "Bear", "HiVol", "LoVol", "Range"])
    fig.update_layout(**PLOTLY_LAYOUT, height=600,
                      title=f"{symbol} {timeframe} — Regime Detection ({model_short})")
    return fig


# ─── TAB 2 : STATE PROBABILITIES ─────────────────────────────────────────────

def state_probability_chart(df: pd.DataFrame, probs: np.ndarray) -> go.Figure:
    n_cols = min(probs.shape[1], 5)
    fig = go.Figure()
    for i in range(n_cols):
        color     = PALETTE[i]
        fill_rgba = _rgba(color, 0.13)          # rgba() — Plotly-safe transparency
        name      = f"State {i} ({REGIMES.get(i, REGIMES[4]).label})"
        fig.add_trace(go.Scatter(
            x=df.index, y=probs[:, i],
            mode="lines", fill="tozeroy", name=name,
            line=dict(color=color, width=1.2),
            fillcolor=fill_rgba,
        ))
    fig.update_layout(**PLOTLY_LAYOUT, height=350,
                      title="Posterior State Probabilities over Time",
                      yaxis_title="P(state | observations)")
    return fig


def transition_matrix_chart(regime_ids: np.ndarray) -> go.Figure:
    n_r   = 5
    trans = np.zeros((n_r, n_r))
    for i in range(1, len(regime_ids)):
        trans[regime_ids[i - 1], regime_ids[i]] += 1
    row_sums = trans.sum(axis=1, keepdims=True)
    trans_p  = np.where(row_sums > 0, trans / row_sums, 0)

    rnames = [f"{REGIMES[i].icon}{REGIMES[i].label[:5]}" for i in range(n_r)]
    fig = go.Figure(go.Heatmap(
        z=trans_p, x=rnames, y=rnames,
        colorscale=[[0, "#0a0e1a"], [0.5, "#1e3a5f"], [1, "#6366f1"]],
        text=np.round(trans_p, 2), texttemplate="%{text:.2f}", showscale=True,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300, title="Transition Probabilities")
    return fig


def regime_duration_chart(regime_ids: np.ndarray) -> go.Figure:
    durations: dict[int, list] = {r: [] for r in range(5)}
    run_r = regime_ids[0]; run_l = 1
    for i in range(1, len(regime_ids)):
        if regime_ids[i] == run_r:
            run_l += 1
        else:
            durations[run_r].append(run_l)
            run_r = regime_ids[i]; run_l = 1
    durations[run_r].append(run_l)

    labels   = [REGIMES[r].label for r in range(5)]
    avg_durs = [np.mean(durations[r]) if durations[r] else 0 for r in range(5)]
    colors   = [REGIME_COLORS[r] for r in range(5)]

    fig = go.Figure(go.Bar(
        x=labels, y=avg_durs, marker_color=colors,
        text=[f"{v:.0f}" for v in avg_durs],
        textposition="outside", textfont=dict(color="#e2e8f0", size=11),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      title="Avg Duration per Regime (bars)", showlegend=False)
    return fig


# ─── TAB 3 : EQUITY CURVE ────────────────────────────────────────────────────

def equity_curve_chart(
    df: pd.DataFrame,
    equity: pd.Series,
    benchmark: pd.Series,
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=benchmark, mode="lines",
                              name="Buy & Hold",
                              line=dict(color="#64748b", width=1.5, dash="dot")))
    fig.add_trace(go.Scatter(x=df.index, y=equity, mode="lines",
                              name="Regime Strategy",
                              line=dict(color="#6366f1", width=2)))
    # Fill under equity curve — use rgba() not 8-digit hex
    fig.add_trace(go.Scatter(
        x=df.index, y=equity,
        fill="tozeroy",
        fillcolor=_rgba("#6366f1", 0.09),
        mode="none", showlegend=False,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320,
                      title="Strategy vs. Buy & Hold Equity Curve",
                      yaxis_title="Normalised Equity")
    return fig


def drawdown_chart(df: pd.DataFrame, equity: pd.Series) -> go.Figure:
    dd = (equity / equity.cummax() - 1) * 100
    fig = go.Figure(go.Scatter(
        x=df.index, y=dd,
        fill="tozeroy",
        fillcolor=_rgba("#ff4d6d", 0.09),
        mode="lines",
        line=dict(color="#ff4d6d", width=1.2),
        name="DD%",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=240, yaxis_title="%")
    return fig


def return_distribution_chart(returns: pd.Series) -> go.Figure:
    r_pct = returns[returns != 0] * 100
    fig   = go.Figure(go.Histogram(x=r_pct, nbinsx=50,
                                    marker_color="#6366f1", opacity=0.8,
                                    name="Strategy Returns"))
    fig.add_vline(x=0, line=dict(color="#64748b", dash="dash", width=1))
    fig.update_layout(**PLOTLY_LAYOUT, height=240,
                      xaxis_title="Return (%)", yaxis_title="Freq")
    return fig


# ─── TAB 4 : FEATURES ────────────────────────────────────────────────────────

def volatility_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_20"] * 100, mode="lines",
                              line=dict(color="#f59e0b", width=1.5), name="Vol 20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_5"] * 100, mode="lines",
                              line=dict(color="#ff4d6d", width=1, dash="dot"), name="Vol 5"))
    fig.update_layout(**PLOTLY_LAYOUT, height=260,
                      title="Rolling Volatility (%)", yaxis_title="%")
    return fig


def rsi_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(x=df.index, y=df["rsi_14"], mode="lines",
                                line=dict(color="#a78bfa", width=1.5), name="RSI 14"))
    fig.add_hline(y=70, line=dict(color="#ff4d6d", dash="dash", width=1))
    fig.add_hline(y=30, line=dict(color="#00d97e", dash="dash", width=1))
    fig.update_layout(**PLOTLY_LAYOUT, height=260, title="RSI (14)")
    fig.update_yaxes(range=[0, 100])
    return fig


def trend_strength_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df.index, y=df["trend_strength"] * 100,
        mode="lines", fill="tozeroy",
        fillcolor=_rgba("#38bdf8", 0.08),        # 8-digit hex not valid in Plotly
        line=dict(color="#38bdf8", width=1.5),
        name="Trend Strength",
    ))
    fig.add_hline(y=0, line=dict(color="#64748b", width=1))
    fig.update_layout(**PLOTLY_LAYOUT, height=260,
                      title="Trend Strength (Price vs MA50, %)")
    return fig


def bb_width_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(x=df.index, y=df["bb_width"] * 100, mode="lines",
                                line=dict(color="#00d97e", width=1.5), name="BB Width"))
    fig.update_layout(**PLOTLY_LAYOUT, height=260, title="Bollinger Band Width (%)")
    return fig


def correlation_heatmap(df: pd.DataFrame, feature_cols: list[str]) -> go.Figure:
    corr = df[feature_cols].corr()
    fig  = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0, "#ff4d6d"], [0.5, "#0a0e1a"], [1, "#00d97e"]],
        zmid=0, zmin=-1, zmax=1,
        text=np.round(corr.values, 2), texttemplate="%{text:.2f}", showscale=True,
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=340, title="Feature Correlation Matrix")
    return fig