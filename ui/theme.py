"""
ui/theme.py
───────────
Global Streamlit CSS injection.  Call inject_css() once at page load.
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --bg:     #0a0e1a;
    --card:   #111827;
    --border: #1e2a3a;
    --text:   #e2e8f0;
    --muted:  #64748b;
    --bull:   #00d97e;
    --bear:   #ff4d6d;
    --high:   #f59e0b;
    --low:    #38bdf8;
    --range:  #a78bfa;
    --accent: #6366f1;
}
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}
section[data-testid="stSidebar"] {
    background: #0d1526 !important;
    border-right: 1px solid var(--border);
}
.regime-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.regime-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 12px 0 0 12px;
}
.regime-card.bull::before  { background: var(--bull); }
.regime-card.bear::before  { background: var(--bear); }
.regime-card.high::before  { background: var(--high); }
.regime-card.low::before   { background: var(--low); }
.regime-card.range::before { background: var(--range); }
.section-header {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}
.info-box {
    background: #161d2e;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    margin-top: 8px;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
