import pandas as pd
from pathlib import Path
import io

def run(cfg=None):
    ROOT      = Path(__file__).resolve().parents[1]
    DATA_DIR  = ROOT / "data"
    DATA_DIR.mkdir(exist_ok=True)
    tidy_csv  = DATA_DIR / "invoices_clean.csv"

    uploaded_file = cfg.get("uploaded_file", None)

    if uploaded_file:
        # If run from Streamlit, uploaded_file will be a file-like object
        df = pd.read_csv(uploaded_file)
    else:
        # Fallback to mock data
        mock_path = DATA_DIR / "mock_invoices.csv"
        if not mock_path.exists():
            raise FileNotFoundError("No uploaded file provided and mock_invoices.csv not found.")
        df = pd.read_csv(mock_path)

    # Standardize column names
    df.columns = (df.columns
                    .str.strip()
                    .str.lower()
                    .str.replace(' ', '_')
                    .str.replace('-', '_'))

    # Convert columns to correct types
    df['date'] = pd.to_datetime(df['date'], format="%m/%d/%y", errors='coerce')
    df['shipped_weight'] = pd.to_numeric(df['shipped_weight'], errors='coerce')

    REQUIRED_COLS = ['account_name', 'date', 'shipped_weight', 'net_sales']
    missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required column(s): {', '.join(missing_cols)}")

    df['net_sales'] = (
        df['net_sales'].astype(str)
            .str.replace(r'[$,()]', '', regex=True)
            .astype(float)
    )

    # Drop unnecessary columns
    df = df.loc[:, ~df.columns.str.contains('^unnamed', case=False)]
    df = df.drop_duplicates(['account_name', 'date', 'shipped_weight', 'net_sales'])

    df.to_csv(tidy_csv, index=False)
    print(f"Step 00: Cleaned data saved to {tidy_csv.name} with {len(df):,} rows.")
