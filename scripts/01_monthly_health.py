# 01_monthly_health.py – Generate monthly customer KPIs and tier labels

from pathlib import Path
import pandas as pd
import numpy as np

def run(cfg=None):
    # Set paths relative to the root
    ROOT      = Path(__file__).resolve().parents[1]
    DATA_DIR  = ROOT / "data"
    OUT_DIR   = ROOT / "outputs"
    OUT_DIR.mkdir(exist_ok=True)

    data_file = DATA_DIR / "invoices_clean.csv"
    out_csv   = OUT_DIR / "customer_health_full.csv"

    # Load cleaned invoice data
    invoices = pd.read_csv(data_file, parse_dates=["date"])

    # 1 – Monthly totals
    monthly = (
        invoices.groupby(["account_name", invoices["date"].dt.to_period("M")])
        .agg(tons=("shipped_weight", "sum"),
             net_sales=("net_sales", "sum"))
        .reset_index()
        .rename(columns={"date": "month"})
    )
    monthly["month"] = monthly["month"].dt.to_timestamp()
    monthly = monthly.sort_values(["account_name", "month"])

    # 2 – Rolling 6-month averages and gaps
    def rolling_avg(series, window=6):
        return series.rolling(window, min_periods=1).mean()

    monthly["avg6m_tons"]  = monthly.groupby("account_name")["tons"].transform(rolling_avg)
    monthly["avg6m_sales"] = monthly.groupby("account_name")["net_sales"].transform(rolling_avg)
    monthly["gap_days"]    = monthly.groupby("account_name")["month"].diff().dt.days.fillna(0)
    monthly["median_gap"]  = monthly.groupby("account_name")["gap_days"].transform("median")

    # 3 – Assign tiers
    TIER_RULES = {
        "Black":  {"drop": 0.50, "gap": 9.0},
        "Red":    {"drop": 0.70, "gap": 3.0},
        "Yellow": {"drop": 0.85, "gap": 1.75},
        "Blue":   {"rise": 1.35, "gap": -30},
        "Green":  {"rise": 1.25, "gap": -20},
        "Light-Green": {"rise": 1.10, "gap": -10}
    }

    def safe_div(n, d):
        return n / d if d and not pd.isna(d) else 1.0

    def assign_alert_tier(r):
        drop = min(safe_div(r.tons, r.avg6m_tons), safe_div(r.net_sales, r.avg6m_sales))
        gap  = r.gap_days / r.median_gap if r.median_gap else 0
        for tier in ["Black", "Red", "Yellow"]:
            rule = TIER_RULES[tier]
            if drop < rule["drop"] or gap > rule["gap"]:
                return tier
        return None

    def assign_growth_tier(r):
        rise = max(safe_div(r.tons, r.avg6m_tons), safe_div(r.net_sales, r.avg6m_sales))
        gap  = r.gap_days - r.median_gap
        for tier in ["Blue", "Green", "Light-Green"]:
            rule = TIER_RULES[tier]
            if rise >= rule["rise"] and gap <= rule["gap"]:
                return tier
        return None

    monthly["alert_tier"]  = monthly.apply(assign_alert_tier, axis=1)
    monthly["growth_tier"] = monthly.apply(assign_growth_tier, axis=1)
    monthly.loc[monthly["alert_tier"].notna(), "growth_tier"] = None

    # 4 – Final health label
    HEALTH_ORDER = {"Black":0,"Red":1,"Yellow":2,"Blue":3,"Green":4,"Light-Green":5}
    mask = monthly[["alert_tier", "growth_tier"]].notna().any(axis=1)

    health_df = (
        monthly[mask]
        .assign(tier_label = lambda d: d.alert_tier.fillna(d.growth_tier),
                tier_rank  = lambda d: d.tier_label.map(HEALTH_ORDER))
        .sort_values(["tier_rank", "tons", "net_sales"], ascending=[True, False, False])
        .drop(columns="tier_rank")
    )

    # 5 – Cadence label
    acct_stats = (
        invoices.groupby("account_name")
        .agg(n_invoices=("account_name", "count"),
             n_months = ("date", lambda s: s.dt.to_period("M").nunique()))
        .reset_index()
    )
    med_gap = monthly[["account_name", "median_gap"]].drop_duplicates("account_name")
    acct_stats = acct_stats.merge(med_gap, on="account_name", how="left")

    acct_stats["buyer_type"] = np.where(
        (acct_stats.median_gap <= 40) &
        ((acct_stats.n_invoices >= 3) | (acct_stats.n_months >= 2)),
        "regular", "sporadic"
    )

    health_df = health_df.merge(acct_stats[["account_name", "buyer_type"]],
                                 on="account_name", how="left")

    health_df.to_csv(out_csv, index=False)
    print(f"Step 01 done: wrote {len(health_df):,} rows to {out_csv.name}")
