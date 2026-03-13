"""
app.py
──────
Market Regime + Strategy Switching Model
Entry point — run with:  streamlit run app.py

All heavy logic is delegated to submodules:
  config/    — constants, settings
  data/      — MT5 loader
  features/  — indicator engineering
  models/    — HMM / GMM / K-Means + regime mapper
  strategy/  — per-regime signal logic
  backtest/  — vectorised P&L engine
  ui/        — Streamlit components, charts, tabs
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st

# ── Page must be configured before any other st calls ────────────────────────
st.set_page_config(
    page_title="Market Regime Switching",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config.constants  import FEATURE_COLS
from config.settings   import AppSettings
from data.loader       import load_ohlcv
from features.engineer import engineer_features
from models            import get_model, map_to_semantic_regimes
from strategy.signals  import generate_signals
from backtest.engine   import run_backtest
from utils.scaler      import scale_features
from ui                import inject_css, render_sidebar, tabs
from ui.components     import (
    section_header, metric_card, regime_card,
    regime_distribution_bars, strategy_matrix_table,
)
from config.constants  import REGIMES


# ─── GLOBAL STYLES ───────────────────────────────────────────────────────────
inject_css()


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
settings, run_btn = render_sidebar()


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="margin-bottom:28px;">'
    '<div style="font-family:\'JetBrains Mono\',monospace;font-size:24px;'
    'font-weight:700;color:#e2e8f0;letter-spacing:-0.5px;">'
    "Market Regime + Strategy Switching</div>"
    '<div style="font-size:13px;color:#64748b;margin-top:4px;">'
    "HMM · GMM · K-Means  ·  Regime-adaptive execution  ·  Quant Validation System"
    "</div></div>",
    unsafe_allow_html=True,
)


# ─── PIPELINE DIAGRAM ────────────────────────────────────────────────────────
section_header("PIPELINE ARCHITECTURE")
pipe_cols = st.columns(7)
pipe_steps = [
    ("📊", "Market Data",  f"{settings.symbol} {settings.timeframe}"),
    ("→",  "",             ""),
    ("⚙️", "Features",    "Returns · Vol · RSI"),
    ("→",  "",             ""),
    ("🧠", "Regime Model", settings.model_short),
    ("→",  "",             ""),
    ("🎯", "Strategy",     "Auto-select"),
]
for col, (icon, title, sub) in zip(pipe_cols, pipe_steps):
    with col:
        if icon == "→":
            st.markdown(
                '<div style="text-align:center;font-size:24px;color:#1e2a3a;'
                'padding-top:16px;">→</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="background:#111827;border:1px solid #1e2a3a;'
                f'border-radius:10px;padding:14px 10px;text-align:center;">'
                f'<div style="font-size:20px;margin-bottom:4px;">{icon}</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
                f'font-weight:600;color:#e2e8f0;">{title}</div>'
                f'<div style="font-size:10px;color:#64748b;margin-top:2px;">{sub}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

st.markdown("<br>", unsafe_allow_html=True)


# ─── PIPELINE EXECUTION ──────────────────────────────────────────────────────

def run_pipeline(cfg: AppSettings) -> dict:
    """
    Full pipeline: data → features → regime detection → signals → backtest.
    Returns a results dict stored in st.session_state.
    """
    # 1. Load data
    df_raw = load_ohlcv(cfg.symbol, cfg.timeframe, cfg.n_bars)

    # 2. Feature engineering
    df = engineer_features(df_raw)

    # 3. Scale features
    X_scaled, _ = scale_features(df[FEATURE_COLS].values)

    # 4. Regime detection
    model      = get_model(cfg.model_type, cfg.n_states)
    raw_states, probs = model.fit_predict(X_scaled)

    # 5. Semantic regime mapping
    regime_ids    = map_to_semantic_regimes(raw_states, df)
    regime_series = pd.Series(regime_ids, index=df.index)

    # 6. Signal generation
    signals = generate_signals(df, regime_series)

    # 7. Backtest
    result = run_backtest(df, signals, cfg.slippage)

    return {
        "df":            df,
        "regime_series": regime_series,
        "regime_ids":    regime_ids,
        "probs":         probs,
        "signals":       signals,
        "result":        result,
    }


# Run on first load or when button pressed
if "state" not in st.session_state or run_btn:
    with st.spinner("Running pipeline…"):
        st.session_state["state"]    = run_pipeline(settings)
        st.session_state["settings"] = settings

state    = st.session_state["state"]
df           = state["df"]
regime_series= state["regime_series"]
regime_ids   = state["regime_ids"]
probs        = state["probs"]
result       = state["result"]
current_rid  = int(regime_series.iloc[-1])


# ─── OVERVIEW ROW ────────────────────────────────────────────────────────────

col_regime, col_stats = st.columns([1, 2])

with col_regime:
    section_header("CURRENT REGIME")
    regime_card(current_rid)
    section_header("REGIME DISTRIBUTION", margin_top="16px")
    regime_distribution_bars(regime_series)

with col_stats:
    section_header("STRATEGY PERFORMANCE")
    c1, c2, c3, c4 = st.columns(4)
    perf_metrics = [
        (c1, "Total Return",  f"{result.total_return*100:+.1f}%",  result.total_return > 0),
        (c2, "Ann. Return",   f"{result.ann_return*100:+.1f}%",    result.ann_return > 0),
        (c3, "Sharpe Ratio",  f"{result.sharpe:.2f}",              result.sharpe > 1),
        (c4, "Max Drawdown",  f"{result.max_drawdown*100:.1f}%",   None),
    ]
    for col, label, val, positive in perf_metrics:
        color = "#f59e0b" if positive is None else ("#00d97e" if positive else "#ff4d6d")
        with col:
            st.markdown(metric_card(label, val, color), unsafe_allow_html=True)

    section_header("STRATEGY MATRIX", margin_top="4px")
    strategy_matrix_table(current_rid)

st.markdown("<br>", unsafe_allow_html=True)


# ─── ANALYSIS TABS ───────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Price + Regimes",
    "🧠 State Probabilities",
    "💹 Equity Curve",
    "📊 Feature Analysis",
])

with tab1:
    tabs.render_price_tab(df, regime_ids, settings.symbol,
                          settings.timeframe, settings.model_short)

with tab2:
    tabs.render_probability_tab(df, regime_ids, probs)

with tab3:
    tabs.render_equity_tab(df, result, regime_series)

with tab4:
    tabs.render_features_tab(df)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
    f'color:#2d3d50;text-align:center;padding:8px 0;">'
    f"QUANT VALIDATION SYSTEM · MARKET REGIME ENGINE · "
    f"{settings.symbol} {settings.timeframe} · {len(df)} BARS · "
    f"{settings.model_short.upper()}"
    f"</div>",
    unsafe_allow_html=True,
)
