"""
data_cleaning.py
Day 2: Clean and validate all 10 datasets. Saves clean CSVs to data/processed/.
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def clean_nav_history() -> pd.DataFrame:
    df = pd.read_csv(RAW / "02_nav_history.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["amfi_code", "date"])

    # Forward-fill missing NAV for weekends/holidays
    full_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="B")
    codes = df["amfi_code"].unique()
    idx = pd.MultiIndex.from_product([codes, full_dates], names=["amfi_code", "date"])
    df = df.set_index(["amfi_code", "date"]).reindex(idx).groupby(level=0).ffill().reset_index()

    df = df[df["nav"] > 0].dropna(subset=["nav"])
    df.to_csv(PROCESSED / "clean_nav_history.csv", index=False)
    print(f"  nav_history     : {len(df):,} rows → clean_nav_history.csv")
    return df


def clean_investor_transactions() -> pd.DataFrame:
    df = pd.read_csv(RAW / "08_investor_transactions.csv")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    df = df[df["amount_inr"] > 0]
    df = df[df["kyc_status"].isin(["Verified", "Pending"])]
    df = df.drop_duplicates()
    df.to_csv(PROCESSED / "clean_investor_transactions.csv", index=False)
    print(f"  transactions    : {len(df):,} rows → clean_investor_transactions.csv")
    return df


def clean_scheme_performance() -> pd.DataFrame:
    df = pd.read_csv(RAW / "07_scheme_performance.csv")
    numeric_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                    "alpha", "beta", "sharpe_ratio", "sortino_ratio",
                    "std_dev_ann_pct", "max_drawdown_pct", "expense_ratio_pct"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["expense_ratio_pct"].between(0.1, 2.5)]
    df.to_csv(PROCESSED / "clean_scheme_performance.csv", index=False)
    print(f"  scheme_perf     : {len(df):,} rows → clean_scheme_performance.csv")
    return df


def clean_fund_master() -> pd.DataFrame:
    df = pd.read_csv(RAW / "01_fund_master.csv")
    df["launch_date"] = pd.to_datetime(df["launch_date"])
    df["fund_house"] = df["fund_house"].str.strip()
    df["scheme_name"] = df["scheme_name"].str.strip()
    df.to_csv(PROCESSED / "clean_fund_master.csv", index=False)
    print(f"  fund_master     : {len(df):,} rows → clean_fund_master.csv")
    return df


def clean_aum() -> pd.DataFrame:
    df = pd.read_csv(RAW / "03_aum_by_fund_house.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.drop_duplicates()
    df.to_csv(PROCESSED / "clean_aum_by_fund_house.csv", index=False)
    print(f"  aum_by_house    : {len(df):,} rows → clean_aum_by_fund_house.csv")
    return df


def clean_sip_inflows() -> pd.DataFrame:
    df = pd.read_csv(RAW / "04_monthly_sip_inflows.csv")
    df["month"] = pd.to_datetime(df["month"])
    # yoy_growth_pct nulls for first 12 months are expected — fill with 0
    df["yoy_growth_pct"] = df["yoy_growth_pct"].fillna(0.0)
    df.to_csv(PROCESSED / "clean_monthly_sip_inflows.csv", index=False)
    print(f"  sip_inflows     : {len(df):,} rows → clean_monthly_sip_inflows.csv")
    return df


def clean_category_inflows() -> pd.DataFrame:
    df = pd.read_csv(RAW / "05_category_inflows.csv")
    df["month"] = pd.to_datetime(df["month"])
    df = df.drop_duplicates()
    df.to_csv(PROCESSED / "clean_category_inflows.csv", index=False)
    print(f"  category_inflows: {len(df):,} rows → clean_category_inflows.csv")
    return df


def clean_folio_count() -> pd.DataFrame:
    df = pd.read_csv(RAW / "06_industry_folio_count.csv")
    df["month"] = pd.to_datetime(df["month"])
    df.to_csv(PROCESSED / "clean_industry_folio_count.csv", index=False)
    print(f"  folio_count     : {len(df):,} rows → clean_industry_folio_count.csv")
    return df


def clean_portfolio_holdings() -> pd.DataFrame:
    df = pd.read_csv(RAW / "09_portfolio_holdings.csv")
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"])
    df = df[df["weight_pct"] > 0]
    df = df.drop_duplicates()
    df.to_csv(PROCESSED / "clean_portfolio_holdings.csv", index=False)
    print(f"  portfolio       : {len(df):,} rows → clean_portfolio_holdings.csv")
    return df


def clean_benchmark_indices() -> pd.DataFrame:
    df = pd.read_csv(RAW / "10_benchmark_indices.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    df = df.drop_duplicates(subset=["date", "index_name"])
    df = df[df["close_value"] > 0]
    df.to_csv(PROCESSED / "clean_benchmark_indices.csv", index=False)
    print(f"  benchmark       : {len(df):,} rows → clean_benchmark_indices.csv")
    return df


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print("  DATA CLEANING — All 10 Datasets")
    print(f"{'='*55}\n")

    clean_fund_master()
    clean_nav_history()
    clean_aum()
    clean_sip_inflows()
    clean_category_inflows()
    clean_folio_count()
    clean_scheme_performance()
    clean_investor_transactions()
    clean_portfolio_holdings()
    clean_benchmark_indices()

    print(f"\n  ✓ All clean CSVs saved to data/processed/")
    print(f"\n{'='*55}")
    print("  Day 2 — Cleaning Complete")
    print(f"{'='*55}\n")
