# Bluestock Fintech — Mutual Fund Analytics Capstone

**Domain:** Mutual Fund / Fintech  
**Duration:** 7 Days | ~50-55 Hours  
**Stack:** Python, Pandas, SQLite, Power BI, Matplotlib, Seaborn, Plotly  
**Author:** Soham Joshi (Physics0070) | June 2026

---

## Project Overview

End-to-end Mutual Fund Analytics Platform that ingests AMFI public data, transforms it via a Python ETL pipeline, stores it in SQLite, and presents insights via an interactive Power BI dashboard.

---

## Setup

```bash
git clone https://github.com/Physics0070/capstone-project.git
cd bluestock_mf_capstone
pip install -r requirements.txt
```

---

## How to Run the ETL Pipeline

Run all steps at once:
```bash
python run_pipeline.py
```

Or run individually:
```bash
python scripts/data_ingestion.py       # Load and inspect all 10 CSVs
python scripts/live_nav_fetch.py       # Fetch live NAV from mfapi.in (needs internet)
python scripts/data_cleaning.py        # Clean all datasets → data/processed/
python scripts/db_load.py              # Load into SQLite → data/db/bluestock_mf.db
python scripts/EDA_Analysis.py         # Generate 15 EDA charts → reports/eda_charts/
python scripts/Performance_Analytics.py # Compute risk metrics → data/processed/
python scripts/Advanced_Analytics.py   # VaR, cohort, HHI → data/processed/
python scripts/recommender.py          # Fund recommendations by risk appetite
```

---

## How to Open the Dashboard

1. Open Power BI Desktop
2. File → Open → `dashboard/bluestock_mf_dashboard.pbix`
3. If data doesn't load: Home → Transform Data → update file paths to your local `data/processed/` folder

---

## Folder Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/           ← 10 original CSV datasets
│   ├── processed/     ← cleaned CSVs + fund_scorecard.csv + alpha_beta.csv
│   └── db/            ← bluestock_mf.db (SQLite, excluded from Git)
├── scripts/
│   ├── data_ingestion.py
│   ├── live_nav_fetch.py
│   ├── data_cleaning.py
│   ├── db_load.py
│   ├── EDA_Analysis.py
│   ├── Performance_Analytics.py
│   ├── Advanced_Analytics.py
│   └── recommender.py
├── sql/
│   ├── schema.sql
│   ├── queries.sql
│   └── data_dictionary.md
├── dashboard/
│   └── bluestock_mf_dashboard.pbix
├── reports/
│   ├── eda_charts/        ← 15 PNG charts
│   ├── Final_Report.docx
│   └── Presentation.pptx
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## Datasets (data/raw/)

| File | Rows | Description |
|------|------|-------------|
| 01_fund_master.csv | 40 | 40 mutual fund schemes with AMFI codes |
| 02_nav_history.csv | 46,000 | Daily NAV Jan 2022 to May 2026 |
| 03_aum_by_fund_house.csv | 90 | Quarterly AUM by fund house |
| 04_monthly_sip_inflows.csv | 48 | Monthly SIP inflow data |
| 05_category_inflows.csv | 144 | Net inflows by fund category |
| 06_industry_folio_count.csv | 21 | Industry folio milestones |
| 07_scheme_performance.csv | 40 | Risk-return metrics per scheme |
| 08_investor_transactions.csv | 32,778 | SIP/Lumpsum/Redemption transactions |
| 09_portfolio_holdings.csv | 322 | Top equity holdings per fund |
| 10_benchmark_indices.csv | 8,050 | Nifty 50, Nifty 100, BSE SmallCap daily |

---

## Key Results

- **Top Fund:** ICICI Pru Mid Cap — Score 84.5, 3yr CAGR 30.44%, Sharpe 1.18
- **SIP Growth:** Rs.11,517 Cr (Jan 2022) → Rs.31,002 Cr (Dec 2025) — 2.7x growth
- **Folio Growth:** 13.26 Cr → 26.12 Cr — doubled in 4 years
- **Highest Risk Fund:** SBI MF Small Cap — daily VaR -2.69%
- **Most Concentrated Portfolio:** Axis MF — HHI 2,064 (heavy IT exposure)

---

## Data Sources

- AMFI India: [amfiindia.com](https://www.amfiindia.com)
- mfapi.in: [api.mfapi.in](https://api.mfapi.in)
- NSE India: [nseindia.com](https://www.nseindia.com)

*All data is publicly available and used for educational purposes only.*
