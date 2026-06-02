"""
data_ingestion.py
Day 1 Task: Load all 10 CSV datasets, inspect shape/dtypes/head, validate AMFI codes.
Bluestock Fintech Capstone — Mutual Fund Analytics Platform
"""

import pandas as pd
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

DATASETS = {
    "fund_master":         "01_fund_master.csv",
    "nav_history":         "02_nav_history.csv",
    "aum_by_fund_house":   "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows":    "05_category_inflows.csv",
    "industry_folio_count":"06_industry_folio_count.csv",
    "scheme_performance":  "07_scheme_performance.csv",
    "investor_transactions":"08_investor_transactions.csv",
    "portfolio_holdings":  "09_portfolio_holdings.csv",
    "benchmark_indices":   "10_benchmark_indices.csv",
}


def load_all() -> dict[str, pd.DataFrame]:
    """Load all 10 CSVs from data/raw and return as a dict of DataFrames."""
    dfs = {}
    for key, filename in DATASETS.items():
        path = RAW / filename
        df = pd.read_csv(path)
        dfs[key] = df
        print(f"\n{'='*60}")
        print(f"  {filename}")
        print(f"  Shape  : {df.shape[0]:,} rows x {df.shape[1]} cols")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Dtypes :\n{df.dtypes.to_string()}")
        print(f"\n  Head (2 rows):")
        print(df.head(2).to_string(index=False))

        # Flag nulls
        null_counts = df.isnull().sum()
        nulls = null_counts[null_counts > 0]
        if not nulls.empty:
            print(f"\n  ⚠ Nulls found:\n{nulls.to_string()}")
        else:
            print(f"\n  ✓ No nulls")
    return dfs


def validate_amfi_codes(dfs: dict[str, pd.DataFrame]) -> None:
    """Check every amfi_code in fund_master exists in nav_history."""
    print(f"\n{'='*60}")
    print("  AMFI CODE VALIDATION")
    print(f"{'='*60}")

    master_codes = set(dfs["fund_master"]["amfi_code"].unique())
    nav_codes    = set(dfs["nav_history"]["amfi_code"].unique())

    in_master_not_nav = master_codes - nav_codes
    in_nav_not_master = nav_codes - master_codes

    print(f"  fund_master  unique codes : {len(master_codes)}")
    print(f"  nav_history  unique codes : {len(nav_codes)}")

    if in_master_not_nav:
        print(f"\n  ⚠ In fund_master but MISSING from nav_history ({len(in_master_not_nav)}): {in_master_not_nav}")
    else:
        print(f"\n  ✓ All fund_master codes present in nav_history")

    if in_nav_not_master:
        print(f"\n  ⚠ In nav_history but MISSING from fund_master ({len(in_nav_not_master)}): {in_nav_not_master}")
    else:
        print(f"\n  ✓ All nav_history codes present in fund_master")


def explore_fund_master(dfs: dict[str, pd.DataFrame]) -> None:
    """Print unique fund houses, categories, sub-categories, risk grades."""
    fm = dfs["fund_master"]
    print(f"\n{'='*60}")
    print("  FUND MASTER EXPLORATION")
    print(f"{'='*60}")
    print(f"\n  Fund Houses ({fm['fund_house'].nunique()}):")
    for fh in sorted(fm["fund_house"].unique()):
        print(f"    - {fh}")

    print(f"\n  Categories: {sorted(fm['category'].unique())}")
    print(f"\n  Sub-categories: {sorted(fm['sub_category'].unique())}")
    print(f"\n  Risk Grades: {sorted(fm['risk_category'].unique())}")
    print(f"\n  Plans: {sorted(fm['plan'].unique())}")


def data_quality_summary(dfs: dict[str, pd.DataFrame]) -> None:
    """Print a compact data quality summary."""
    print(f"\n{'='*60}")
    print("  DATA QUALITY SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Dataset':<30} {'Rows':>8} {'Cols':>5} {'Nulls':>8} {'Dupes':>8}")
    print(f"  {'-'*62}")
    for key, df in dfs.items():
        nulls  = df.isnull().sum().sum()
        dupes  = df.duplicated().sum()
        print(f"  {key:<30} {df.shape[0]:>8,} {df.shape[1]:>5} {nulls:>8,} {dupes:>8,}")


if __name__ == "__main__":
    dfs = load_all()
    explore_fund_master(dfs)
    validate_amfi_codes(dfs)
    data_quality_summary(dfs)
    print(f"\n{'='*60}")
    print("  Day 1 — Data Ingestion Complete")
    print(f"{'='*60}\n")
