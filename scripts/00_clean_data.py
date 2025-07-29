# scripts/00_clean_data.py

import pandas as pd
from pathlib import Path

def run(cfg=None):
    ROOT = Path(__file__).resolve().parents[1]
    DATA_DIR = ROOT / "data"
    tidy_csv = DATA_DIR / "invoices_clean.csv"

    # If user uploaded a file in the Streamlit app
    if cfg and "uploaded_file" in cfg and cfg["uploaded_file"] is not None:
        raw_csv = cfg["uploaded_file"]  # This is a StringIO object in Streamlit
        df = pd.read_csv(raw_csv)
    else:
        raw_csv_path = DATA_DIR / "mock_invoices.csv"
        if not raw_csv_path.exists():
            raise FileNotFoundError(f"Missing fallback mock data at {raw_csv_path}")
        df = pd.read_csv(raw_csv_path)

    # Standardize column names
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace('-', '_')
    )

    # Validate required columns
    REQUIRED_COLS = ['account_name', 'date', 'shipped_weight', 'net_sales']
    missing = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['shipped_weight'] = pd.to_numeric(df['shipped_weight'], errors='coerce')
    df['net_sales'] = pd.to_numeric(df['net_sales'], errors='coerce')

    df = df.drop_duplicates()
    df = df.loc[:, ~df.columns.str.contains('^unnamed', case=False)]

    df.to_csv(tidy_csv, index=False)
    print(f"✅ Step 00 complete: wrote {len(df):,} rows to {tidy_csv.name}")