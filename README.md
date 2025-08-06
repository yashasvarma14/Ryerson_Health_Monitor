# Ryerson Customer Health Monitor

![Python](https://img.shields.io/badge/Python-3.9-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![License: MIT](https://img.shields.io/badge/License-MIT-blue)

[Ryerson Monitor Streamlit App](https://ryersonhealthmonitor.streamlit.app/)

A data-driven dashboard built during my Sales Analytics internship at Ryerson Metals to track and visualize customer health trends using Python, Plotly, and simple machine learning. Designed to be non-technical rep-friendly, actionable, and installable anywhere with just a CSV upload.

*This version has the mock data option for privacy reasons. The actual version was developed using real Ryerson invoice data and delivered to their internal team.

## Who I built this for

Ryerson's inside sales reps are incredibly busy. They juggle dozens of accounts and don’t always have a clear view of which customers are quietly pulling back or which ones are rapidly growing.

I built this tool to give them that visibility.


## What it does

This monitor lets any rep:
- Upload their monthly invoice data (through CSV)
- See a clean dashboard showing each customer’s health over time
- Get alerted about accounts at risk of declining
- Understand changes in sales, shipped tons, and customer ordering cadence
- Export a simple list of which customers to follow up with and why


## What's under the hood

`00_clean_data.py` - Cleans raw invoice data (if not already clean) 
`01_monthly_health.py` - Calculates monthly KPIs and assigns health tiers 
`02_visual_data.py` - Builds a filterable HTML dashboard
`03_predictive_health.py` - Uses light ML to flag likely declines (logistic regression) 
`04_contact_alerts.py` - Generates a rep-facing call list with tailored messages 

`main.py` - One script to run everything — built for easy future rep use 
`settings.yaml` - Easily adjustable thresholds for tiers, thresholds, and logic 
`outputs/` - Where all final reports and dashboards are saved 
`data/` - Where you drop your input invoice CSV 

---

## Technologies Used

- Python - all logic, analysis, and output
- Pandas - data work
- Plotly - interactive dashboards (using HTML)
- Scikit-learn - basic logistic regression for decline prediction
- YAML - makes thresholds editable for future users
- Streamlit App & GitHub - full version control and portability

---

## How to Use (2 Ways)

### Option 1: Use it online (No coding/install)  
Go to the hosted app and either:

- Upload your invoice CSV  
- Or click “Run with Mock Data” to test with sample inputs
- [Streamlit App Link](https://ryersonhealthmonitor.streamlit.app/)

### Option 2: Run Locally

1. Clone this repo
   Or download it manually from GitHub and open it in VS Code

2. Drop your invoice CSV into the `data/` folder  
   Use a cleaned file like `invoices_clean.csv` (must have `account_name`, `date`, `net_sales`, `shipped_weight`)

3. Adjust rules in `settings.yaml`  
   Want some tier to trigger at a custom % instead of the default? Do that here.

4. Run the main script.

5. Open the outputs/ folder to view:
    Final health scores
    Visual dashboards
    Rep call lists with custom messages
    ML predictions of future decline

## About Me
    Yashas Varma
    Sales Analytics Intern @ Ryerson Metals
    B.S. in Economics, Texas A&M University
    Aspiring MSBA grad & technical storyteller

    This project taught me how to combine:
    Business intuition
    Analytics tools
    Lightweight ML
    Communication that helps

    If you’d like to talk about data storytelling, analytics, or hiring me— feel free to connect.
