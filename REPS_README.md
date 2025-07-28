Ryerson Customer Health Monitor – For Sales Reps

This will help you quickly spot which customers are growing, shrinking, or need attention.

1. Drop your invoice CSV file into the /data folder  
   - Make sure the file has these columns:
     `account_name`, `date`, `net_sales`, `shipped_weight`

2. Open settings.yaml
   - Update the line that starts with `raw_csv:` to match your file name  
     raw_csv: data/my_invoices_July2025.csv

3. Run this one command:
   python main.py

The tool will clean your data, analyze customer behavior, predict churn risk, and save these outputs to `/outputs`:

- `customer_dashboard.html` – interactive graph by customer
- `customer_decline_probs.csv` – whats their risk scores
- `rep_contact_list.csv` – who to call and why

To open your dashboard, just double-click the HTML file or upload to a browser.