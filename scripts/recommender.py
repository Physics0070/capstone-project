"""
recommender.py
Day 6: Simple fund recommender based on investor risk appetite.
Usage: python scripts/recommender.py
"""

import pandas as pd
from pathlib import Path

PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"

RISK_MAP = {
    "Low":      ["Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    score = pd.read_csv(PROCESSED / "fund_scorecard.csv")
    fm    = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    merged = score.merge(fm[["amfi_code", "risk_category"]], on="amfi_code", how="left")

    valid_grades = RISK_MAP.get(risk_appetite.title())
    if not valid_grades:
        print(f"  Invalid input. Choose from: Low, Moderate, High")
        return pd.DataFrame()

    filtered = merged[merged["risk_category"].isin(valid_grades)]
    top = filtered.nlargest(top_n, "sharpe")[
        ["scheme_name", "fund_house", "sub_category", "risk_category",
         "cagr_3yr", "sharpe", "alpha", "score"]
    ].reset_index(drop=True)
    top.index += 1
    return top


def main():
    print(f"\n{'='*60}")
    print("  FUND RECOMMENDER — Bluestock MF Capstone")
    print(f"{'='*60}")

    for appetite in ["Low", "Moderate", "High"]:
        print(f"\n  Risk Appetite: {appetite.upper()}")
        print(f"  {'-'*55}")
        result = recommend(appetite)
        if result.empty:
            print("  No funds found.")
            continue
        for i, r in result.iterrows():
            print(f"  {i}. {r['scheme_name'][:40]}")
            print(f"     Fund House : {r['fund_house']}")
            print(f"     Category   : {r['sub_category']} | Risk: {r['risk_category']}")
            print(f"     3yr CAGR   : {r['cagr_3yr']}%  Sharpe: {r['sharpe']}  Score: {r['score']}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
