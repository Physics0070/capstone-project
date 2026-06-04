"""
Performance_Analytics.py
Day 4: Fund Performance Analytics
Run: python scripts/Performance_Analytics.py
Deliverables: fund_scorecard.csv, alpha_beta.csv, benchmark_comparison.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
from pathlib import Path

BASE      = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
REPORTS   = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

RF = 0.065 / 252  # RBI repo rate 6.5% annualised → daily

plt.rcParams.update({
    "figure.dpi": 120,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
    "axes.grid": True,
    "grid.alpha": 0.4,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def load_data():
    nav   = pd.read_csv(PROCESSED / "clean_nav_history.csv",        parse_dates=["date"])
    bench = pd.read_csv(PROCESSED / "clean_benchmark_indices.csv",  parse_dates=["date"])
    fm    = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    return nav, bench, fm


def compute_daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    nav = nav.sort_values(["amfi_code", "date"])
    nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
    return nav


def compute_cagr(nav_series: pd.Series, date_series: pd.Series, years: int) -> float:
    end_date   = date_series.max()
    start_date = end_date - pd.DateOffset(years=years)
    subset     = nav_series[date_series >= start_date]
    if len(subset) < 20:
        return np.nan
    n_days = len(subset)
    return (subset.iloc[-1] / subset.iloc[0]) ** (252 / n_days) - 1


def compute_sharpe(returns: pd.Series) -> float:
    excess = returns - RF
    if returns.std() == 0:
        return np.nan
    return (excess.mean() / returns.std()) * np.sqrt(252)


def compute_sortino(returns: pd.Series) -> float:
    excess       = returns - RF
    downside     = returns[returns < 0]
    downside_std = downside.std()
    if downside_std == 0:
        return np.nan
    return (excess.mean() / downside_std) * np.sqrt(252)


def compute_max_drawdown(nav_series: pd.Series):
    running_max = nav_series.cummax()
    drawdown    = nav_series / running_max - 1
    max_dd      = drawdown.min()
    dd_date     = drawdown.idxmin()
    return max_dd, dd_date


def compute_alpha_beta(fund_returns: pd.Series, bench_returns: pd.Series):
    merged = pd.concat([fund_returns, bench_returns], axis=1).dropna()
    if len(merged) < 30:
        return np.nan, np.nan
    slope, intercept, r, p, se = stats.linregress(merged.iloc[:, 1], merged.iloc[:, 0])
    beta  = slope
    alpha = intercept * 252  # annualised
    return alpha, beta


def build_metrics(nav: pd.DataFrame, bench: pd.DataFrame, fm: pd.DataFrame) -> pd.DataFrame:
    nifty100 = bench[bench["index_name"] == "NIFTY100"].set_index("date")["close_value"]
    nifty100_ret = nifty100.pct_change().dropna()

    records = []
    for code, grp in nav.groupby("amfi_code"):
        grp      = grp.sort_values("date").set_index("date")
        ret      = grp["daily_return"].dropna()
        nav_vals = grp["nav"]

        cagr_1  = compute_cagr(nav_vals, nav_vals.index.to_series(), 1)
        cagr_3  = compute_cagr(nav_vals, nav_vals.index.to_series(), 3)
        cagr_5  = compute_cagr(nav_vals, nav_vals.index.to_series(), 5)
        sharpe  = compute_sharpe(ret)
        sortino = compute_sortino(ret)
        max_dd, dd_date = compute_max_drawdown(nav_vals)
        alpha, beta = compute_alpha_beta(ret, nifty100_ret)

        fund_info = fm[fm["amfi_code"] == code].iloc[0]
        records.append({
            "amfi_code":       code,
            "scheme_name":     fund_info["scheme_name"],
            "fund_house":      fund_info["fund_house"],
            "sub_category":    fund_info["sub_category"],
            "plan":            fund_info["plan"],
            "expense_ratio":   fund_info["expense_ratio_pct"],
            "cagr_1yr":        round(cagr_1  * 100, 2) if not np.isnan(cagr_1)  else np.nan,
            "cagr_3yr":        round(cagr_3  * 100, 2) if not np.isnan(cagr_3)  else np.nan,
            "cagr_5yr":        round(cagr_5  * 100, 2) if not np.isnan(cagr_5)  else np.nan,
            "sharpe":          round(sharpe,  4) if not np.isnan(sharpe)  else np.nan,
            "sortino":         round(sortino, 4) if not np.isnan(sortino) else np.nan,
            "max_drawdown_pct":round(max_dd  * 100, 2),
            "max_dd_date":     str(dd_date.date()) if pd.notnull(dd_date) else "",
            "alpha":           round(alpha * 100, 4) if not np.isnan(alpha) else np.nan,
            "beta":            round(beta,  4) if not np.isnan(beta)  else np.nan,
        })

    return pd.DataFrame(records)


def build_scorecard(metrics: pd.DataFrame) -> pd.DataFrame:
    df = metrics.copy()

    # Higher = better: cagr_3yr, sharpe, alpha
    # Lower  = better: expense_ratio, max_drawdown_pct (most negative = worst)
    df["rank_cagr3"]    = df["cagr_3yr"].rank(ascending=True,  pct=True) * 100
    df["rank_sharpe"]   = df["sharpe"].rank(ascending=True,    pct=True) * 100
    df["rank_alpha"]    = df["alpha"].rank(ascending=True,     pct=True) * 100
    df["rank_expense"]  = df["expense_ratio"].rank(ascending=False, pct=True) * 100  # lower is better
    df["rank_maxdd"]    = df["max_drawdown_pct"].rank(ascending=False, pct=True) * 100  # less negative = better

    df["score"] = (
        0.30 * df["rank_cagr3"] +
        0.25 * df["rank_sharpe"] +
        0.20 * df["rank_alpha"] +
        0.15 * df["rank_expense"] +
        0.10 * df["rank_maxdd"]
    ).round(2)

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


def compute_tracking_error(fund_returns: pd.Series, bench_returns: pd.Series) -> float:
    merged = pd.concat([fund_returns, bench_returns], axis=1).dropna()
    diff   = merged.iloc[:, 0] - merged.iloc[:, 1]
    return diff.std() * np.sqrt(252) * 100  # annualised %


def plot_benchmark_comparison(nav: pd.DataFrame, bench: pd.DataFrame,
                               scorecard: pd.DataFrame, fm: pd.DataFrame):
    top5_codes = scorecard.head(5)["amfi_code"].tolist()

    nifty50  = bench[bench["index_name"] == "NIFTY50"].sort_values("date")
    nifty100 = bench[bench["index_name"] == "NIFTY100"].sort_values("date")

    # Use last 3 years
    cutoff = nav["date"].max() - pd.DateOffset(years=3)

    fig, ax = plt.subplots(figsize=(13, 6))

    for code in top5_codes:
        grp   = nav[(nav["amfi_code"] == code) & (nav["date"] >= cutoff)].sort_values("date")
        label = fm.loc[fm["amfi_code"] == code, "fund_house"].values[0]
        norm  = grp["nav"] / grp["nav"].iloc[0] * 100
        ax.plot(grp["date"], norm, linewidth=1.5, label=label)

    for idx_df, idx_name, lw, ls in [
        (nifty50,  "Nifty 50",  2.5, "--"),
        (nifty100, "Nifty 100", 2.5, ":"),
    ]:
        idx_sub  = idx_df[idx_df["date"] >= cutoff]
        idx_norm = idx_sub["close_value"] / idx_sub["close_value"].iloc[0] * 100
        ax.plot(idx_sub["date"], idx_norm, linewidth=lw, linestyle=ls,
                color="black", label=idx_name, alpha=0.8)

    ax.set_title("Top 5 Funds vs Nifty 50 & Nifty 100 (3-Year, Rebased to 100)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Indexed Value (Base = 100)")
    ax.legend(fontsize=8, loc="upper left")
    path = REPORTS / "benchmark_comparison.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ benchmark_comparison.png saved")


def print_summary(scorecard: pd.DataFrame):
    print(f"\n  TOP 10 FUNDS BY SCORECARD:")
    print(f"  {'Rank':<5} {'Fund House':<20} {'SubCat':<15} {'CAGR3':<8} {'Sharpe':<8} {'Alpha':<8} {'Score':<7}")
    print(f"  {'-'*75}")
    for _, r in scorecard.head(10).iterrows():
        print(f"  {int(r['rank']):<5} {str(r['fund_house'])[:19]:<20} {str(r['sub_category'])[:14]:<15} "
              f"{r['cagr_3yr']:<8} {r['sharpe']:<8} {r['alpha']:<8} {r['score']:<7}")


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print("  PERFORMANCE ANALYTICS — Day 4")
    print(f"{'='*55}\n")

    nav, bench, fm = load_data()
    nav = compute_daily_returns(nav)

    print("  Computing metrics for all 40 funds...")
    metrics   = build_metrics(nav, bench, fm)
    scorecard = build_scorecard(metrics)

    # Save fund_scorecard.csv
    scorecard_path = PROCESSED / "fund_scorecard.csv"
    scorecard.to_csv(scorecard_path, index=False)
    print(f"  ✓ fund_scorecard.csv saved ({len(scorecard)} funds)")

    # Save alpha_beta.csv
    ab_cols   = ["amfi_code", "scheme_name", "fund_house", "sub_category", "alpha", "beta", "sharpe", "sortino"]
    ab_path   = PROCESSED / "alpha_beta.csv"
    scorecard[ab_cols].to_csv(ab_path, index=False)
    print(f"  ✓ alpha_beta.csv saved")

    # Benchmark chart
    plot_benchmark_comparison(nav, bench, scorecard, fm)

    # Tracking error for top 5
    nifty100     = bench[bench["index_name"] == "NIFTY100"].set_index("date")["close_value"]
    nifty100_ret = nifty100.pct_change().dropna()
    print(f"\n  TRACKING ERROR vs Nifty 100 (top 5 funds):")
    for code in scorecard.head(5)["amfi_code"]:
        grp  = nav[nav["amfi_code"] == code].sort_values("date").set_index("date")
        ret  = grp["daily_return"].dropna()
        te   = compute_tracking_error(ret, nifty100_ret)
        name = fm.loc[fm["amfi_code"] == code, "fund_house"].values[0]
        print(f"    {name[:25]:<25} TE = {te:.2f}%")

    print_summary(scorecard)

    print(f"\n{'='*55}")
    print("  Day 4 — Performance Analytics Complete")
    print(f"{'='*55}\n")
