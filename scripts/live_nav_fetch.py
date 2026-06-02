"""
live_nav_fetch.py
Day 1 Task: Fetch live NAV from mfapi.in for 5 selected schemes.
Saves each scheme's NAV history as a raw CSV in data/raw/.
Bluestock Fintech Capstone — Mutual Fund Analytics Platform
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

# ── Config ─────────────────────────────────────────────────────────────────────
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
BASE_URL = "https://api.mfapi.in/mf/{code}"

SCHEMES = {
    125497: "HDFC Top 100 Direct Growth",
    119551: "SBI Bluechip Regular Growth",
    120503: "ICICI Pru Bluechip Direct Growth",
    118632: "Nippon Large Cap Direct Growth",
    119092: "Axis Bluechip Direct Growth",
    120841: "Kotak Bluechip Direct Growth",
}


def fetch_nav(amfi_code: int, scheme_name: str) -> pd.DataFrame | None:
    """Fetch full NAV history for one scheme from mfapi.in."""
    url = BASE_URL.format(code=amfi_code)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"  ✗ {scheme_name} ({amfi_code}): Request failed — {e}")
        return None
    except json.JSONDecodeError:
        print(f"  ✗ {scheme_name} ({amfi_code}): Invalid JSON response")
        return None

    nav_data = data.get("data", [])
    if not nav_data:
        print(f"  ✗ {scheme_name} ({amfi_code}): Empty data returned")
        return None

    df = pd.DataFrame(nav_data)
    df.columns = ["date", "nav"]
    df["amfi_code"] = amfi_code
    df["scheme_name"] = scheme_name
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"])
    df = df.sort_values("date").reset_index(drop=True)
    df = df[["amfi_code", "scheme_name", "date", "nav"]]
    return df


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    all_frames = []

    print(f"\n{'='*60}")
    print("  LIVE NAV FETCH — mfapi.in")
    print(f"{'='*60}")

    for code, name in SCHEMES.items():
        print(f"\n  Fetching: {name} (AMFI {code})")
        df = fetch_nav(code, name)
        if df is not None:
            out_path = RAW_DIR / f"live_nav_{code}.csv"
            df.to_csv(out_path, index=False)
            all_frames.append(df)
            print(f"  ✓ {len(df):,} rows | Latest NAV: {df['nav'].iloc[-1]:.4f} on {df['date'].iloc[-1].date()}")
            print(f"    Saved → {out_path.name}")
        time.sleep(0.5)  # polite rate limiting

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined_path = RAW_DIR / "live_nav_all_schemes.csv"
        combined.to_csv(combined_path, index=False)
        print(f"\n  ✓ Combined file saved → {combined_path.name}")
        print(f"    Total rows: {len(combined):,}")

    print(f"\n{'='*60}")
    print("  Live NAV Fetch Complete")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
