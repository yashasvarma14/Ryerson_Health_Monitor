import streamlit as st
import pandas as pd
import os
from pathlib import Path
import shutil
import yaml
import importlib.util
import sys
import io

st.set_page_config(page_title="Ryerson Customer Health Monitor", layout="centered")

st.title("Ryerson Customer Health Monitor")
st.markdown("Upload your latest Sales/Invoices csv file below and we’ll process it end-to-end.")

uploaded_file = st.file_uploader("Upload your invoice CSV", type=["csv"])
cfg = {}

if uploaded_file:
    # Save it to disk
    data_path = Path("data/dallas_invoices.csv")
    with open(data_path, "wb") as f:
        f.write(uploaded_file.read())

    # Rewind file stream and load into memory for processing
    uploaded_file.seek(0)
    csv_memory_file = io.StringIO(uploaded_file.getvalue().decode("utf-8"))

    st.success("File uploaded successfully!")

    # Load config
    with open("settings.yaml") as f:
        cfg = yaml.safe_load(f)

    # Pass uploaded file into cfg
    cfg["uploaded_file"] = csv_memory_file

    # Run scripts
    scripts = [
        "scripts/00_clean_data.py",
        "scripts/01_monthly_health.py",
        "scripts/02_visual_data.py",
        "scripts/03_predictive_health.py",
        "scripts/04_contact_alerts.py",
    ]

    for path in scripts:
        st.write(f"Running {Path(path).name} ...")
        spec = importlib.util.spec_from_file_location(Path(path).stem, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[Path(path).stem] = module
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            module.run(cfg)
        else:
            st.warning(f"{path} has no run() function")

    # Download links
    st.markdown("### Done! Download Your Outputs Below:")

    for file in Path("outputs").glob("*.csv"):
        st.download_button(f"Download {file.name}", file.read_bytes(), file.name)

    for file in Path("outputs").glob("*.html"):
        st.download_button(f"Download {file.name}", file.read_bytes(), file.name)