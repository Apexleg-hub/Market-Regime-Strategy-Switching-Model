"""
ui/sidebar.py
─────────────
Renders the left sidebar and returns a populated AppSettings object.
"""

import streamlit as st

from config.constants import SYMBOLS, TIMEFRAMES, MODEL_OPTIONS
from config.settings  import AppSettings


def render_sidebar() -> tuple[AppSettings, bool]:
    """
    Render sidebar widgets.

    Returns
    -------
    settings : AppSettings
    run      : bool — True when the user clicks ▶ RUN MODEL
    """
    with st.sidebar:
        st.markdown(
            '<div style="font-family:JetBrains Mono;font-size:18px;'
            'font-weight:700;color:#e2e8f0;margin-bottom:4px;">📡 REGIME ENGINE</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:11px;color:#64748b;margin-bottom:24px;'
            'letter-spacing:1px;">MARKET SWITCHING SYSTEM v1.0</div>',
            unsafe_allow_html=True,
        )

        _section("DATA SOURCE · MT5")
        symbol    = st.selectbox("Symbol",    SYMBOLS,     index=0)
        timeframe = st.selectbox("Timeframe", TIMEFRAMES,  index=0)
        n_bars    = st.slider("Bars", 200, 1000, 500, 50)

        _section("DETECTION MODEL", margin_top=True)
        model_type = st.selectbox("Algorithm", MODEL_OPTIONS)
        n_states   = st.slider("States / Clusters", 3, 7, 5)

        _section("EXECUTION", margin_top=True)
        slippage_bps = st.slider("Slippage (bps)", 0, 10, 2)
        run_btn      = st.button(" RUN MODEL", use_container_width=True,
                                 type="primary")

        st.markdown("---")
        st.markdown(
            '<div class="info-box">'
            "Loads cached pkl data.<br>No live MT5 connection needed.<br>"
            f"Symbols: {' · '.join(SYMBOLS)}<br>"
            f"Timeframes: {' · '.join(TIMEFRAMES[:3])}"
            "</div>",
            unsafe_allow_html=True,
        )

    settings = AppSettings(
        symbol=symbol,
        timeframe=timeframe,
        n_bars=n_bars,
        model_type=model_type,
        n_states=n_states,
        slippage_bps=float(slippage_bps),
    )
    return settings, run_btn


def _section(label: str, margin_top: bool = False) -> None:
    style = 'style="margin-top:20px;"' if margin_top else ""
    st.markdown(
        f'<div class="section-header" {style}>{label}</div>',
        unsafe_allow_html=True,
    )
