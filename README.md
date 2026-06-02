# Bluestock Fintech — Mutual Fund Analytics Capstone

**Domain:** Mutual Fund / Fintech  
**Duration:** 7 Days | ~50-55 Hours  
**Stack:** Python, Pandas, SQLite, Power BI, Matplotlib, Seaborn, Plotly

---

## Project Overview

End-to-end Mutual Fund Analytics Platform that ingests AMFI public data, transforms it via a Python ETL pipeline, stores it in SQLite, and presents insights via an interactive Power BI dashboard.

---

## Folder Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/           ← Original CSVs (10 datasets + live NAV fetches)
│   ├── processed/     ← Cleaned, merged CSVs
│   └── db/            ← bluestock_mf.db (SQLite)
├── notebooks/         ← Jupyter notebooks (EDA, performance, advanced analytics)
├── scripts/           ← Python scripts (ETL, metrics, recommender)
├── sql/               ← schema.sql + queries.sql
├── dashboard/         ← Power BI .pbix file
├── reports/           ← Final PDF report + Presentation
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/physics_007/capstone-project.git
cd bluestock_mf_capstone
pip install -r requirements.txt
```

---

## Running the ETL Pipeline

```bash
# Day 1: Ingest all 10 datasets
python scripts/data_ingestion.py

# Day 1: Fetch live NAV from mfapi.in (requires internet)
python scripts/live_nav_fetch.py
```

---

## Datasets (data/raw/)

| File | Rows | Description |
|------|------|-------------|
| 01_fund_master.csv | 40 | Master list of 40 schemes |
| 02_nav_history.csv | 46,000 | Daily NAV Jan 2022 - May 2026 |
| 03_aum_by_fund_house.csv | 90 | Quarterly AUM by fund house |
| 04_monthly_sip_inflows.csv | 48 | Monthly SIP inflow data |
| 05_category_inflows.csv | 144 | Net inflows by category |
| 06_industry_folio_count.csv | 21 | Industry folio count milestones |
| 07_scheme_performance.csv | 40 | Risk-return metrics per scheme |
| 08_investor_transactions.csv | 32,778 | SIP/Lumpsum/Redemption transactions |
| 09_portfolio_holdings.csv | 322 | Top equity holdings per fund |
| 10_benchmark_indices.csv | 8,050 | Nifty 50, Nifty 100, BSE SmallCap daily |

---

## Data Sources

- AMFI India: [amfiindia.com](https://www.amfiindia.com)
- mfapi.in: [api.mfapi.in](https://api.mfapi.in)
- NSE India: [nseindia.com](https://www.nseindia.com)

---

## Deliverables

| Day | Deliverable |
|-----|-------------|
| 1 | `data_ingestion.py`, `live_nav_fetch.py`, GitHub repo |
| 2 | `bluestock_mf.db`, `schema.sql`, `queries.sql` |
| 3 | `EDA_Analysis.ipynb` with 15+ charts |
| 4 | `Performance_Analytics.ipynb`, `fund_scorecard.csv` |
| 5 | `bluestock_mf_dashboard.pbix`, `Dashboard.pdf` |
| 6 | `Advanced_Analytics.ipynb`, `recommender.py` |
| 7 | `Final_Report.pdf`, `Presentation.pptx` |

---

*Prepared by: Soham | Bluestock Fintech Capstone | June 2026*
