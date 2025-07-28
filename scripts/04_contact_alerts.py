# 04_contact_alerts.py – Generate rep alert list

from pathlib import Path
import pandas as pd
import numpy as np

def run(cfg = None):
    ROOT         = Path(__file__).resolve().parents[1]
    HEALTH_CSV   = ROOT / "outputs" / "customer_health_full.csv"
    RISK_CSV     = ROOT / "outputs" / "customer_decline_probs.csv"
    OUTDIR       = ROOT / "outputs"; OUTDIR.mkdir(exist_ok=True)
    CSV_OUT      = OUTDIR / "rep_contact_list.csv"
    HTML_OUT     = OUTDIR / "rep_contact_list.html"

    QUIET_DAYS   = 45
    SALES_DROP   = -50
    PROB_LIMIT   = 0.60
    MAX_ROWS_OUT = 200

    health = pd.read_csv(HEALTH_CSV, parse_dates=["month"])
    risk   = pd.read_csv(RISK_CSV) if RISK_CSV.exists() else pd.DataFrame()

    latest = (health.sort_values(["account_name", "month"])
                    .groupby("account_name", as_index=False)
                    .tail(1))

    if not risk.empty:
        latest = latest.merge(risk, on="account_name", how="left")

    sales_vs = latest["net_sales"] / latest["avg6m_sales"]
    sales_vs = sales_vs.replace([np.inf, -np.inf], np.nan).fillna(0)
    latest["sales_vs_baseline_%"] = (sales_vs - 1) * 100
    latest["gap_vs_median"] = latest["gap_days"] - latest["median_gap"]

    tier_alert = latest["tier_label"].eq("Black")
    combo_drop = (latest["gap_vs_median"] > QUIET_DAYS) & \
                 (latest["sales_vs_baseline_%"] < SALES_DROP)
    ml_flagged = latest.get("prob_decline", 0) >= PROB_LIMIT

    flagged = latest[tier_alert | combo_drop | ml_flagged].copy()

    tier_score = flagged["tier_label"].map({"Black": 3, "Red": 2, "Yellow": 1}).fillna(0)
    flagged["severity"] = tier_score * 100 \
                        + flagged["gap_vs_median"].clip(lower=0) \
                        + flagged["sales_vs_baseline_%"].clip(upper=0).abs()
    flagged = flagged.sort_values("severity", ascending=False).head(MAX_ROWS_OUT)

    def reason(row):
        if row["tier_label"] == "Black":
            return "Black tier customer"
        if row["gap_vs_median"] > QUIET_DAYS and row["sales_vs_baseline_%"] < SALES_DROP:
            return "Unusual silence + sales drop"
        return "Predicted decline (ML)"

    def make_msg(row):
        arrow = "⬇︎" if row["sales_vs_baseline_%"] < 0 else "⬆︎"
        return (f"{reason(row)} • Last order {int(row['gap_days'])}d "
                f"(typ {int(row['median_gap'])}d) • "
                f"Sales {arrow}{abs(row['sales_vs_baseline_%']):.0f}% vs. norm")

    flagged["rep_message"] = flagged.apply(make_msg, axis=1)

    cols = ["account_name", "tier_label", "gap_days",
            "sales_vs_baseline_%", "prob_decline", "rep_message"]

    flagged[cols].to_csv(CSV_OUT, index=False)

    html_table = (flagged[cols]
                  .style.set_table_styles([{"selector": "th", "props": [("text-align", "left")]}])
                  .format({"sales_vs_baseline_%": "{:+.1f}%", "prob_decline": "{:.2f}"})
                  .hide(axis="index")
                  .to_html())

    HTML_OUT.write_text(f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Rep Alerts</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 6px 8px; }}
th {{ background: #f0f0f0; }}
</style></head><body>
<h2>Customers That May Need Attention ({len(flagged)})</h2>
{html_table}
</body></html>""", encoding="utf-8")

    print(f"Step 04 done: wrote {len(flagged)} alerts to {CSV_OUT.name} and {HTML_OUT.name}")
