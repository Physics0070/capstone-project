"""
db_load.py
Day 2: Load all cleaned CSVs into SQLite database (bluestock_mf.db).
"""

import sqlite3
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"
DB_DIR    = Path(__file__).resolve().parent.parent / "data" / "db"
SCHEMA    = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"
DB_PATH   = DB_DIR / "bluestock_mf.db"

DB_DIR.mkdir(parents=True, exist_ok=True)


def build_dim_date(engine, nav_df: pd.DataFrame) -> None:
    dates = nav_df["date"].drop_duplicates().sort_values()
    dim = pd.DataFrame({"date": dates})
    dim["year"]       = dim["date"].dt.year
    dim["month"]      = dim["date"].dt.month
    dim["quarter"]    = dim["date"].dt.quarter
    dim["month_name"] = dim["date"].dt.strftime("%B")
    dim["is_weekday"] = (dim["date"].dt.dayofweek < 5).astype(int)
    dim["date"]       = dim["date"].dt.strftime("%Y-%m-%d")
    dim.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"  dim_date        : {len(dim):,} rows loaded")


def compute_daily_returns(nav_df: pd.DataFrame) -> pd.DataFrame:
    nav_df = nav_df.sort_values(["amfi_code", "date"])
    nav_df["daily_return"] = nav_df.groupby("amfi_code")["nav"].pct_change()
    nav_df["date"] = nav_df["date"].dt.strftime("%Y-%m-%d")
    return nav_df


def load_all() -> None:
    # Create schema
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA) as f:
        conn.executescript(f.read())
    conn.close()
    print(f"  Schema created at {DB_PATH.name}\n")

    engine = create_engine(f"sqlite:///{DB_PATH}")

    # dim_fund
    fm = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    fm["launch_date"] = pd.to_datetime(fm["launch_date"]).dt.strftime("%Y-%m-%d")
    fm.to_sql("dim_fund", engine, if_exists="append", index=False)
    print(f"  dim_fund        : {len(fm):,} rows loaded")

    # fact_nav + dim_date
    nav = pd.read_csv(PROCESSED / "clean_nav_history.csv", parse_dates=["date"])
    build_dim_date(engine, nav)
    nav = compute_daily_returns(nav)
    nav.to_sql("fact_nav", engine, if_exists="append", index=False)
    print(f"  fact_nav        : {len(nav):,} rows loaded")

    # fact_transactions
    tx = pd.read_csv(PROCESSED / "clean_investor_transactions.csv")
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"]).dt.strftime("%Y-%m-%d")
    tx.to_sql("fact_transactions", engine, if_exists="append", index=False)
    print(f"  fact_transactions: {len(tx):,} rows loaded")

    # fact_performance
    perf = pd.read_csv(PROCESSED / "clean_scheme_performance.csv")
    perf.to_sql("fact_performance", engine, if_exists="append", index=False)
    print(f"  fact_performance: {len(perf):,} rows loaded")

    # fact_portfolio
    port = pd.read_csv(PROCESSED / "clean_portfolio_holdings.csv")
    port["portfolio_date"] = pd.to_datetime(port["portfolio_date"]).dt.strftime("%Y-%m-%d")
    port.to_sql("fact_portfolio", engine, if_exists="append", index=False)
    print(f"  fact_portfolio  : {len(port):,} rows loaded")

    # fact_aum
    aum = pd.read_csv(PROCESSED / "clean_aum_by_fund_house.csv")
    aum["date"] = pd.to_datetime(aum["date"]).dt.strftime("%Y-%m-%d")
    aum.to_sql("fact_aum", engine, if_exists="append", index=False)
    print(f"  fact_aum        : {len(aum):,} rows loaded")

    # fact_sip_industry
    sip = pd.read_csv(PROCESSED / "clean_monthly_sip_inflows.csv")
    sip["month"] = pd.to_datetime(sip["month"]).dt.strftime("%Y-%m-%d")
    sip.to_sql("fact_sip_industry", engine, if_exists="append", index=False)
    print(f"  fact_sip_industry: {len(sip):,} rows loaded")

    print(f"\n  ✓ Database ready: {DB_PATH}")


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print("  DB LOAD — SQLite")
    print(f"{'='*55}\n")
    load_all()
    print(f"\n{'='*55}")
    print("  Day 2 — DB Load Complete")
    print(f"{'='*55}\n")
