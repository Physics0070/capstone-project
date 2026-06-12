"""
run_pipeline.py
Master script to run the full Bluestock MF Capstone pipeline end-to-end.
Usage: python run_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

BASE    = Path(__file__).resolve().parent
SCRIPTS = BASE / "scripts"

PIPELINE = [
    ("Day 1: Data Ingestion",       SCRIPTS / "data_ingestion.py"),
    ("Day 2: Data Cleaning",        SCRIPTS / "data_cleaning.py"),
    ("Day 2: DB Load",              SCRIPTS / "db_load.py"),
    ("Day 3: EDA Analysis",         SCRIPTS / "EDA_Analysis.py"),
    ("Day 4: Performance Analytics",SCRIPTS / "Performance_Analytics.py"),
    ("Day 6: Advanced Analytics",   SCRIPTS / "Advanced_Analytics.py"),
    ("Day 6: Fund Recommender",     SCRIPTS / "recommender.py"),
]


def run_step(label: str, script: Path) -> bool:
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")
    result = subprocess.run([sys.executable, str(script)], capture_output=False)
    if result.returncode != 0:
        print(f"\n  ERROR in {script.name} — pipeline stopped.")
        return False
    return True


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print("  BLUESTOCK MF CAPSTONE — FULL PIPELINE")
    print(f"{'='*55}")

    for label, script in PIPELINE:
        if not run_step(label, script):
            sys.exit(1)

    print(f"\n{'='*55}")
    print("  ALL STEPS COMPLETE")
    print("  Outputs in data/processed/ and reports/")
    print(f"{'='*55}\n")
