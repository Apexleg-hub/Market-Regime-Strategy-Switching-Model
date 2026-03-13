"""
ui/components.py
────────────────
Reusable HTML/Plotly building blocks used across multiple tabs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from config.constants import REGIMES, REGIME_COLORS


def section_header(label: str, margin_top: str = "0px") -> None:
    st.markdown(
        f'<div class="section-header" style="margin-top:{margin_top};">{label}</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, color: str) -> str:
    return (
        f'<div style="background:#111827;border:1px solid #1e2a3a;'
        f'border-radius:10px;padding:16px;text-align:center;margin-bottom:12px;">'
        f'<div style="font-size:22px;font-weight:600;font-family:\'JetBrains Mono\','
        f'monospace;color:{color};">{value}</div>'
        f'<div style="font-size:10px;color:#64748b;margin-top:4px;'
        f'text-transform:uppercase;letter-spacing:1px;">{label}</div>'
        f"</div>"
    )


def regime_card(regime_id: int) -> None:
    r = REGIMES[regime_id]
    st.markdown(
        f'<div class="regime-card {r.css_class}">'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
        f'letter-spacing:2px;text-transform:uppercase;color:#64748b;margin-bottom:4px;">'
        f"Detected State</div>"
        f'<div style="font-size:28px;font-weight:600;color:{r.color};">'
        f"{r.icon} {r.label}</div>"
        f'<div style="margin-top:12px;font-size:12px;color:#94a3b8;">Active Strategy</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;'
        f'color:{r.color};margin-top:4px;">{r.strategy}</div>'
        f'<div style="font-size:11px;color:#64748b;margin-top:8px;line-height:1.5;">'
        f"{r.description}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def regime_distribution_bars(regime_series: pd.Series) -> None:
    counts = regime_series.value_counts()
    total  = len(regime_series)
    for rid, r in REGIMES.items():
        pct = counts.get(rid, 0) / total * 100
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
            f'<div style="font-size:13px;width:16px;">{r.icon}</div>'
            f'<div style="font-size:11px;color:#94a3b8;width:90px;'
            f"font-family:'JetBrains Mono',monospace;\">{r.label[:12]}</div>"
            f'<div style="flex:1;background:#1e2a3a;border-radius:4px;height:6px;">'
            f'<div style="width:{pct:.0f}%;background:{r.color};height:6px;'
            f'border-radius:4px;"></div></div>'
            f'<div style="font-size:11px;color:#64748b;font-family:\'JetBrains Mono\','
            f'monospace;width:35px;text-align:right;">{pct:.0f}%</div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def strategy_matrix_table(current_regime: int) -> None:
    rows = ""
    for rid, r in REGIMES.items():
        active = "→" if rid == current_regime else ""
        bg     = "#161d2e" if rid == current_regime else "transparent"
        rows += (
            f'<tr style="background:{bg};">'
            f'<td style="padding:8px 12px;font-size:13px;">{r.icon} {r.label}</td>'
            f'<td style="padding:8px 12px;font-size:11px;font-family:\'JetBrains Mono\',monospace;">'
            f'<span style="background:{r.color}22;color:{r.color};'
            f'border:1px solid {r.color}44;padding:3px 10px;border-radius:12px;">'
            f"{r.strategy}</span></td>"
            f'<td style="padding:8px 12px;font-size:11px;color:#64748b;">{active}</td>'
            f"</tr>"
        )
    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;">'
        f'<thead><tr style="border-bottom:1px solid #1e2a3a;">'
        f'<th style="text-align:left;padding:8px 12px;font-size:10px;color:#64748b;'
        f'letter-spacing:2px;text-transform:uppercase;">Regime</th>'
        f'<th style="text-align:left;padding:8px 12px;font-size:10px;color:#64748b;'
        f'letter-spacing:2px;text-transform:uppercase;">Strategy</th>'
        f'<th style="padding:8px 12px;"></th>'
        f"</tr></thead><tbody>{rows}</tbody></table>",
        unsafe_allow_html=True,
    )
