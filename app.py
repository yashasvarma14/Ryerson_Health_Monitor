import streamlit as st
import pandas as pd
from pathlib import Path
import yaml
import importlib.util
import sys

st.set_page_config(page_title="Ryerson Customer Health Monitor", layout="centered")

st.title("Ryerson Customer Health Monitor")
st.markdown("Upload your latest `dallas_invoices.csv` file **or** try it with mock data.")

# File uploader
uploaded_file = st.file_uploader("Upload your invoice CSV", type=["csv"])
use_mock = st.button("Run with Mock Data")

cfg = {}

if uploaded_file:
    # Save uploaded file to /data/dallas_invoices.csv
    data_path = Path("data/dallas_invoices.csv")
    with open(data_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    # Load YAML settings and override raw_csv path
    with open("settings.yaml") as f:
        cfg = yaml.safe_load(f)
    cfg["raw_csv"] = str(data_path)

elif use_mock:
    st.info("Using built-in mock data.")
    with open("settings.yaml") as f:
        cfg = yaml.safe_load(f)

    # settings.yaml should already have raw_csv preset to mock data path
    cfg["raw_csv"] = "data/mock_invoices.csv"

else:
    st.stop()

# Run scripts
scripts = [
    "scripts/00_clean_data.py",
    "scripts/01_monthly_health.py",
    "scripts/02_visual_data.py",
    "scripts/03_predictive_health.py",
    "scripts/04_contact_alerts.py",
]

for path in scripts:
    st.write(f"Running `{path.split('/')[-1]}` ...")
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

# Output section
st.markdown("### Done! Download Your Outputs:")
for file in Path("outputs").glob("*.csv"):
    st.download_button(f"Download {file.name}", file.read_bytes(), file.name)

for file in Path("outputs").glob("*.html"):
    st.download_button(f"Download {file.name}", file.read_bytes(), file.name)
