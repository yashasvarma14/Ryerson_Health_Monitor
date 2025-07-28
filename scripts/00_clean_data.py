# 00_clean_data.py — clean raw invoices into a tidy format
# --------------------------------------------------------
import pandas as pd
from pathlib import Path

def run(cfg=None):
    ROOT      = Path(__file__).resolve().parents[1]   # …/ryerson_customer_health
    DATA_DIR  = ROOT / "data"
    
    raw_csv   = DATA_DIR / "mock_invoices.csv"         # original monthly file
    tidy_csv  = DATA_DIR / "invoices_clean.csv"             

    df = pd.read_csv(raw_csv)

    # Standardize column names: lowercase, snake_case
    df.columns = (df.columns
                    .str.strip()
                    .str.lower()
                    .str.replace(' ', '_')
                    .str.replace('-', '_'))

    # Convert columns to data types needed
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%y", errors='coerce')
    df['shipped_weight'] = pd.to_numeric(df['shipped_weight'], errors='coerce')
    df['net_sales'] = (df['net_sales'].astype(str)
                                    .str.replace(r'[$,()]', '', regex=True)
                                    .astype(float))

    # Drop any extra columns
    df = df.loc[:, ~df.columns.str.contains('^unnamed', case = False)]

    # Drop duplicates
    df = df.drop_duplicates(['account_name', 'date', 'shipped_weight', 'net_sales'])

    df.to_csv(tidy_csv, index = False)
    print(f"Step 00 done: wrote {len(df):,} rows to {tidy_csv.name}")
