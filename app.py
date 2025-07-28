import streamlit as st
import pandas as pd
import os
from pathlib import Path
import shutil
import yaml
import importlib.util
import sys

st.set_page_config(page_title="Ryerson Customer Health Monitor", layout="centered")

st.title("Ryerson Customer Health Monitor")
st.markdown("Upload your latest `dallas_invoices.csv` file below and we’ll process it end-to-end.")

uploaded_file = st.file_uploader("Upload Dallas Invoices CSV", type="csv")

if uploaded_file:
    data_path = Path("data/dallas_invoices.csv")
    with open(data_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    # Load settings
    with open("settings.yaml") as f:
        cfg = yaml.safe_load(f)
        
    cfg["raw_csv"] = str(data_path)

    # Run all scripts
    scripts = [
        "scripts/00_clean_data.py",
        "scripts/01_monthly_health.py",
        "scripts/02_visual_data.py",
        "scripts/03_predictive_health.py",
        "scripts/04_contact_alerts.py",
    ]

    for path in scripts:
        st.write(f"Running {path.split('/')[-1]} ...")
        path_obj = Path(path)
        name = path_obj.stem
        spec = importlib.util.spec_from_file_location(name, path_obj)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            module.run(cfg)
        else:
            st.warning(f"{name} has no run() function")

    # Show download links
    st.markdown("### Done! Download Your Outputs Below:")
    for file in Path("outputs").glob("*.csv"):
        st.download_button(f"Download {file.name}", file.read_bytes(), file.name)

    for file in Path("outputs").glob("*.html"):
        st.download_button(f"Download {file.name}", file.read_bytes(), file.name)