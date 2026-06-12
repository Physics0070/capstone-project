"""
monte_carlo_simulation.py
Bonus B3: Monte Carlo simulation projecting NAV growth over 5 years with uncertainty bands.
Run: python scripts/monte_carlo_simulation.py
Output: reports/monte_carlo_projection.png, reports/monte_carlo_results.csv
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

BASE      = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
REPORTS   = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

N_SIMULATIONS  = 1000
N_DAYS         = 252 * 5   # 5 years of trading days
CONFIDENCE     = [5, 25, 75, 95]  # percentile bands

plt.rcParams.update({
    "figure.dpi": 120,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def run_monte_carlo(nav_series: pd.Series, n_sims: int, n_days: int):
    """Run Monte Carlo simulation using historical daily returns."""
    returns = nav_series.pct_change().dropna()
    mu      = returns.mean()
    sigma   = returns.std()
    last_nav = nav_series.iloc[-1]

    # Simulate paths: each column is one simulation
    daily_returns = np.random.normal(mu, sigma, (n_days, n_sims))
    price_paths   = last_nav * np.exp(np.cumsum(np.log(1 + daily_returns), axis=0))

    # Prepend starting NAV
    start_row    = np.full((1, n_sims), last_nav)
    price_paths  = np.vstack([start_row, price_paths])
    return price_paths


def plot_simulations(price_paths, fund_name, last_nav, ax, color):
    days  = np.arange(price_paths.shape[0])
    years = days / 252

    p5   = np.percentile(price_paths, 5,  axis=1)
    p25  = np.percentile(price_paths, 25, axis=1)
    p50  = np.percentile(price_paths, 50, axis=1)
    p75  = np.percentile(price_paths, 75, axis=1)
    p95  = np.percentile(price_paths, 95, axis=1)

    ax.fill_between(years, p5,  p95, alpha=0.12, color=color, label="5th-95th pct")
    ax.fill_between(years, p25, p75, alpha=0.25, color=color, label="25th-75th pct")
    ax.plot(years, p50, color=color, linewidth=2.5, label=f"Median: ₹{p50[-1]:,.0f}")
    ax.plot(years, p5,  color=color, linewidth=1,   linestyle="--", alpha=0.6)
    ax.plot(years, p95, color=color, linewidth=1,   linestyle="--", alpha=0.6)
    ax.axhline(last_nav, color="gray", linestyle=":", linewidth=1, alpha=0.7)

    ax.set_title(f"{fund_name}\n(Start NAV: ₹{last_nav:,.2f})", fontsize=11)
    ax.set_xlabel("Years from today")
    ax.set_ylabel("Projected NAV (₹)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    return {"p5": p5[-1], "p25": p25[-1], "p50": p50[-1], "p75": p75[-1], "p95": p95[-1]}


def main():
    print(f"\n{'='*55}")
    print("  MONTE CARLO SIMULATION — Bonus B3")
    print(f"  {N_SIMULATIONS} simulations × {N_DAYS} days (5 years)")
    print(f"{'='*55}\n")

    nav   = pd.read_csv(PROCESSED / "clean_nav_history.csv", parse_dates=["date"])
    score = pd.read_csv(PROCESSED / "fund_scorecard.csv")
    fm    = pd.read_csv(PROCESSED / "clean_fund_master.csv")

    top5_codes = score.head(5)["amfi_code"].tolist()
    colors     = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e"]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    results = []
    np.random.seed(42)

    for i, code in enumerate(top5_codes):
        fund_nav   = nav[nav["amfi_code"] == code].sort_values("date")["nav"]
        fund_house = fm.loc[fm["amfi_code"] == code, "fund_house"].values[0]
        short_name = fund_house.replace(" Mutual Fund", " MF").replace(" MF", " MF")[:20]
        last_nav   = fund_nav.iloc[-1]

        print(f"  Simulating {short_name}...")
        paths = run_monte_carlo(fund_nav, N_SIMULATIONS, N_DAYS)
        stats = plot_simulations(paths, short_name, last_nav, axes[i], colors[i])

        cagr_median = (stats["p50"] / last_nav) ** (1/5) - 1
        results.append({
            "fund_house":   fund_house,
            "current_nav":  round(last_nav, 2),
            "p5_nav_5yr":   round(stats["p5"],  2),
            "p25_nav_5yr":  round(stats["p25"], 2),
            "median_5yr":   round(stats["p50"], 2),
            "p75_nav_5yr":  round(stats["p75"], 2),
            "p95_nav_5yr":  round(stats["p95"], 2),
            "median_cagr":  round(cagr_median * 100, 2),
        })
        print(f"    Current: ₹{last_nav:,.2f} | Median 5yr: ₹{stats['p50']:,.2f} | CAGR: {cagr_median*100:.1f}%")

    # Summary chart in last panel
    ax = axes[5]
    fund_names = [r["fund_house"].replace(" Mutual Fund", "")[:15] for r in results]
    medians    = [r["median_5yr"] for r in results]
    p5s        = [r["p5_nav_5yr"] for r in results]
    p95s       = [r["p95_nav_5yr"] for r in results]
    starts     = [r["current_nav"] for r in results]

    x = np.arange(len(fund_names))
    ax.bar(x, medians, color=colors, alpha=0.8, label="Median 5yr NAV")
    ax.errorbar(x, medians,
                yerr=[np.array(medians) - np.array(p5s),
                      np.array(p95s)    - np.array(medians)],
                fmt="none", color="black", capsize=5, linewidth=1.5)
    ax.scatter(x, starts, color="red", zorder=5, s=50, label="Current NAV")
    ax.set_xticks(x)
    ax.set_xticklabels(fund_names, rotation=20, ha="right", fontsize=9)
    ax.set_title("5-Year NAV Projection Summary\n(bars=median, whiskers=5th-95th pct)")
    ax.set_ylabel("Projected NAV (₹)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
    ax.legend(fontsize=8)

    fig.suptitle(f"Monte Carlo NAV Projection — Top 5 Funds | {N_SIMULATIONS} Simulations | 5-Year Horizon",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    chart_path = REPORTS / "monte_carlo_projection.png"
    fig.savefig(chart_path, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  ✓ monte_carlo_projection.png saved")

    # Save results CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(REPORTS / "monte_carlo_results.csv", index=False)
    print(f"  ✓ monte_carlo_results.csv saved")

    print(f"\n  SIMULATION SUMMARY:")
    print(f"  {'Fund':<22} {'Current NAV':>12} {'Median 5yr':>12} {'CAGR':>8} {'Range (P5-P95)'}")
    print(f"  {'-'*72}")
    for r in results:
        name = r['fund_house'].replace(' Mutual Fund','')[:20]
        print(f"  {name:<22} ₹{r['current_nav']:>10,.2f} ₹{r['median_5yr']:>10,.2f} "
              f"{r['median_cagr']:>7.1f}%  ₹{r['p5_nav_5yr']:,.0f} – ₹{r['p95_nav_5yr']:,.0f}")

    print(f"\n{'='*55}")
    print("  Bonus B3 — Monte Carlo Complete")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
