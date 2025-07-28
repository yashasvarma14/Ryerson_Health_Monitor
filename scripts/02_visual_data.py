# 02_visual_data.py – Visualize customer health and tiers

from pathlib import Path
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

from sklearn.pipeline      import Pipeline
from sklearn.impute        import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model  import LogisticRegression
from sklearn.metrics       import roc_auc_score
from sklearn.model_selection import TimeSeriesSplit

# Absolute paths
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs" / "customer_health_full.csv"
PRED_CSV = ROOT / "outputs" / "customer_decline_probs.csv"
FORECAST = ROOT / "outputs" / "sales_forecast_3m.csv"
OUTDIR = ROOT / "outputs"; OUTDIR.mkdir(exist_ok=True)


health = pd.read_csv(DATA, parse_dates=["month"])

# 1) Paths & data
DATA_FILE = Path("../outputs/customer_health_full.csv")
OUT_DIR   = Path("../outputs"); OUT_DIR.mkdir(exist_ok=True)
HTML_OUT  = OUTDIR / "customer_dashboard.html"


# Every customer name, **sorted alphabetically**
customers = sorted(health["account_name"].unique())

# 2 - Figure factory – one mini‑dashboard per customer
def build_fig(df: pd.DataFrame) -> go.Figure:
    """Return a 3‑row Plotly figure for a single customer."""
    name = df["account_name"].iloc[0]

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        subplot_titles=(
            "Shipped Tons",
            "Net Sales ($)",
            "Health Tier History",
        ),
        row_heights=[0.3, 0.3, 0.4],
        vertical_spacing=0.04,
    )

    # Tons
    fig.add_bar(
        x=df["month"],
        y=df["tons"],
        name="Tons",
        row=1,
        col=1,
        marker_color="steelblue",
        hovertemplate="<b>%{x|%b %Y}</b><br>Tons: %{y}<extra></extra>",
    )

    # Sales (in thousands of $)
    fig.add_bar(
        x=df["month"],
        y=df["net_sales"],
        name="Sales",
        row=2,
        col=1,
        marker_color="darkorange",
        hovertemplate="<b>%{x|%b %Y}</b><br>Sales $%{y:,.0f}<extra></extra>",
    )

    # Tier history
    fig.add_scatter(
        x = df["month"],
        y=df["tier_label"],
        mode="markers",
        row=3,
        col=1,
        marker=dict(color="mediumseagreen", size=9),
        hovertemplate="<b>%{x|%b %Y}</b><br>%{y}<extra></extra>",
    )
    fig.update_yaxes(
        row=3,
        col=1,
        type="category",
        categoryorder="array",
        categoryarray=[
            "Black",
            "Red",
            "Yellow",
            "Light-Green",
            "Green",
            "Blue",
        ],
    )

    fig.update_layout(
        height=740,
        width=960,
        showlegend=False,
        title=dict(text=f"<b>{name}</b>", x=0.01, y=0.95, font=dict(size=22)),
        margin=dict(t=80, l=50, r=30, b=40),
    )
    return fig

# Build a dict {customer to HTML <div>}
html_blocks: dict[str, str] = {}
for cust in customers:
    fig = build_fig(health.query("account_name == @cust"))
    html_blocks[cust] = fig.to_html(full_html=False, include_plotlyjs=False)

# 3 - Write the final HTML file with a dropdown
with HTML_OUT.open("w", encoding="utf8") as f:
    f.write(
        """<!DOCTYPE html>
<html><head>
  <meta charset=\"utf-8\">
  <script src=\"https://cdn.plot.ly/plotly-2.24.2.min.js\"></script>
  <title>Customer Health Dashboard</title>
  <style>
    body  {font-family:Arial,Helvetica,sans-serif;margin:20px;}
    select{font-size:16px;margin-bottom:16px;padding:4px 8px;}
    .page {display:none;padding:10px;border:1px solid #ccc;border-radius:6px;}
  </style>
</head><body>
<h2>Interactive Customer Dashboard</h2>
<label for=\"cust\">Choose a customer:</label>
<select id=\"cust\" onchange=\"showCust()\">\n"""
    )

    # A-Z dropdown clients
    for cust in customers:
        safe = cust.replace(" ", "_").replace("&", "and")
        f.write(f"  <option value='{safe}'>{cust}</option>\n")

    f.write("""</select>
<div id=\"wrap\">\n""")

    # Each customer's figure inside its own div(div is just the identifier)
    for cust, div in html_blocks.items():
        safe = cust.replace(" ", "_").replace("&", "and")
        f.write(f"<div class='page' id='{safe}'>\n{div}\n</div>\n")

    f.write(
        """</div>
<script>
function showCust(){
  var sel = document.getElementById('cust').value;
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
  var el = document.getElementById(sel);
  if(el) el.style.display = 'block';
}
window.onload = () => {document.getElementById('cust').selectedIndex = 0; showCust();};
</script>
</body></html>"""
    )

def run(cfg=None):
    pass 

print(f"Step 02 Done! HTML dashboard written.")