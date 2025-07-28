# 03_predictive_health.py - Flag customers at risk using basic ML

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score

def run(cfg=None):
    # File paths
    ROOT       = Path(__file__).resolve().parents[1]
    DATA_CSV   = ROOT / "outputs" / "customer_health_full.csv"
    OUT_PROBS  = ROOT / "outputs" / "customer_decline_probs.csv"
    LOOKAHEAD_MONTHS = 3
    PROB_THRESHOLD   = 0.45

    if not DATA_CSV.exists():
        raise FileNotFoundError(f"Missing input: {DATA_CSV}")

    # Load and prepare data
    data = pd.read_csv(DATA_CSV, parse_dates = ['month'])
    data = data.sort_values(['account_name', 'month'])

    data['avg3m_sales'] = (
        data.groupby('account_name')['net_sales']
            .transform(lambda s: s.rolling(3, min_periods = 1).mean())
    )
    data['sales_vs_baseline'] = data['net_sales'] / data['avg6m_sales']
    data['label'] = (
        data.groupby('account_name')['sales_vs_baseline']
             .shift(-LOOKAHEAD_MONTHS)
             .lt(0.70)
             .astype(float)
    )

    FEATURES = ['sales_vs_baseline', 'gap_days', 'tons',
                'avg6m_sales', 'avg6m_tons', 'median_gap']

    X_all = data[FEATURES].replace([np.inf, -np.inf], np.nan)
    y_all = data['label']

    mask_train = y_all.notna() & np.isfinite(X_all).all(axis = 1)
    X_train = X_all.loc[mask_train]
    y_train = y_all.loc[mask_train]

    model = Pipeline([
        ('imputer', SimpleImputer(strategy = 'median')),
        ('scaler',  StandardScaler(with_mean = False)),
        ('logreg',  LogisticRegression(max_iter = 1000, class_weight = 'balanced'))
    ])

    # Cross-validation check
    cv = TimeSeriesSplit(n_splits = 4)
    scores = []
    for train_idx, test_idx in cv.split(X_train):
        model.fit(X_train.iloc[train_idx], y_train.iloc[train_idx])
        preds = model.predict_proba(X_train.iloc[test_idx])[:, 1]
        scores.append(roc_auc_score(y_train.iloc[test_idx], preds))
    # Final model fit
    model.fit(X_train, y_train)

    # Predict decline probability on latest row per customer
    latest = (
        data.groupby('account_name', as_index = False)
            .tail(1).reset_index(drop = True)
    )

    X_latest = latest[FEATURES].replace([np.inf, -np.inf], np.nan)
    latest['prob_decline'] = model.predict_proba(X_latest)[:, 1]
    latest['pred_status'] = np.where(
        latest['prob_decline'] >= PROB_THRESHOLD,
        'Likely-Decline', 'Likely-Stable'
    )

    out = latest[['account_name', 'prob_decline', 'pred_status']]
    out.to_csv(OUT_PROBS, index = False)
    print(f"Step 03 done: wrote {len(out):,} rows to {OUT_PROBS.name}")
