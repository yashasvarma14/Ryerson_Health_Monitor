import streamlit as st
import pandas as pd
from pathlib import Path
import yaml
import importlib.util
import sys

st.set_page_config(page_title="Ryerson Customer Health Monitor", layout="centered")

st.title("Ryerson Customer Health Monitor")
st.markdown("Upload your latest `dallas_invoices.csv` file **or** try it with mock data.")

# File uploader and mock button
uploaded_file = st.file_uploader("Upload your invoice CSV", type=["csv"])
use_mock = st.button("Run with Mock Data")

# Sidebar sliders for customization
st.sidebar.header("⚙️ Customize Thresholds")

# Tier thresholds – ALERT
st.sidebar.subheader("Alert Tier Thresholds")
tier_black = st.sidebar.slider("Black Drop Ratio", 0.0, 1.0, 0.50)
tier_red = st.sidebar.slider("Red Drop Ratio", 0.0, 1.0, 0.70)
tier_yellow = st.sidebar.slider("Yellow Drop Ratio", 0.0, 1.0, 0.85)
gap_black = st.sidebar.slider("Black Gap Ratio", 1.0, 10.0, 9.0)
gap_red = st.sidebar.slider("Red Gap Ratio", 1.0, 5.0, 3.0)
gap_yellow = st.sidebar.slider("Yellow Gap Ratio", 1.0, 3.0, 1.75)

# Tier thresholds – GROWTH
st.sidebar.subheader("Growth Tier Thresholds")
tier_light = st.sidebar.slider("Light-Green Rise Ratio", 1.0, 1.2, 1.10)
tier_green = st.sidebar.slider("Green Rise Ratio", 1.0, 1.3, 1.25)
tier_blue = st.sidebar.slider("Blue Rise Ratio", 1.0, 1.5, 1.35)
gap_light = st.sidebar.slider("Light-Green Max Gap", -40, 0, -10)
gap_green = st.sidebar.slider("Green Max Gap", -40, 0, -20)
gap_blue = st.sidebar.slider("Blue Max Gap", -40, 0, -30)

# Other thresholds
st.sidebar.subheader("🔍 Prediction + Alerts")
lookahead_months = st.sidebar.slider("Lookahead Months", 1, 6, 3)
prob_threshold = st.sidebar.slider("Prediction Threshold", 0.0, 1.0, 0.45)
quiet_days = st.sidebar.slider("Quiet Days Threshold", 10, 90, 45)
sales_drop = st.sidebar.slider("Sales Drop %", -100, 0, -50)

# Load settings.yaml
with open("settings.yaml") as f:
    cfg = yaml.safe_load(f)

# Override thresholds with sidebar sliders
cfg["tiers"] = {
    "black_drop": tier_black,
    "red_drop": tier_red,
    "yellow_drop": tier_yellow,
    "black_gap": gap_black,
    "red_gap": gap_red,
    "yellow_gap": gap_yellow,
    "light_rise": tier_light,
    "green_rise": tier_green,
    "blue_rise": tier_blue,
    "light_gap": gap_light,
    "green_gap": gap_green,
    "blue_gap": gap_blue,
}
cfg["label_window"] = lookahead_months
cfg["prob_cut"]     = prob_threshold
cfg["quiet_days"]   = quiet_days
cfg["sales_drop"]   = sales_drop

# Handle uploaded or mock data
if uploaded_file:
    st.success("File uploaded successfully.")
    data_path = Path("data/dallas_invoices.csv")
    with open(data_path, "wb") as f:
        f.write(uploaded_file.read())
    cfg["raw_csv"] = str(data_path)
elif use_mock:
    st.info("Using built-in mock data.")
    cfg["raw_csv"] = "data/mock_invoices.csv"
else:
    st.stop()

# Run all processing scripts
scripts = [
    "scripts/00_clean_data.py",
    "scripts/01_monthly_health.py",
    "scripts/02_visual_data.py",
    "scripts/03_predictive_health.py",
    "scripts/04_contact_alerts.py",
]

for path in scripts:
    st.write(f"Running `{Path(path).name}` ...")
    name = Path(path).stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    try:
        if hasattr(module, "run"):
            module.run(cfg)
        else:
            st.warning(f"{name} has no run() function")
    except Exception as e:
        st.error(f"❌ Error in {name}: {e}")
        st.stop()

# Download outputs
st.markdown("### Done! Download Your Outputs:")
for file in Path("outputs").glob("*.csv"):
    st.download_button(f"Download {file.name}", file.read_bytes(), file.name)

for file in Path("outputs").glob("*.html"):
    st.download_button(f"Download {file.name}", file.read_bytes(), file.name)
