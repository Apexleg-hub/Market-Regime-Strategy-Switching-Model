

regime_switching/
│
├── app.py                      ← Entry point (streamlit run app.py)
├── requirements.txt
├── README.md
│
├── config/
│   ├── constants.py            ← Regime definitions, FEATURE_COLS, Plotly theme
│   └── settings.py             ← AppSettings dataclass
│
├── data/
│   └── loader.py               ← load_ohlcv() — pkl or synthetic fallback
│
├── features/
│   └── engineer.py             ← engineer_features() — all indicators
│
├── models/
│   ├── base.py                 ← BaseRegimeModel ABC
│   ├── hmm_model.py            ← GaussianHMM wrapper
│   ├── gmm_model.py            ← GaussianMixture wrapper
│   ├── kmeans_model.py         ← KMeans + soft assignment
│   ├── regime_mapper.py        ← Raw clusters → semantic regimes
│   └── factory.py              ← get_model(type, n_states)
│
├── strategy/
│   └── signals.py              ← generate_signals() — per-regime dispatch
│
├── backtest/
│   └── engine.py               ← run_backtest() → BacktestResult
│
├── utils/
│   └── scaler.py               ← scale_features()
│
└── ui/
    ├── theme.py                ← inject_css()
    ├── sidebar.py              ← render_sidebar() → AppSettings
    ├── components.py           ← HTML building blocks
    ├── charts.py               ← All Plotly figure builders
    └── tabs.py                 ← render_price_tab / probability / equity / features