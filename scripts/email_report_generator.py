"""
email_report_generator.py
Bonus B5: Automated HTML email report with weekly performance summary.
Run: python scripts/email_report_generator.py
Output: reports/weekly_performance_report.html
To send via email: configure SMTP settings at the bottom.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

BASE      = Path(__file__).resolve().parent.parent
PROCESSED = BASE / "data" / "processed"
REPORTS   = BASE / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)


def load_data():
    score = pd.read_csv(PROCESSED / "fund_scorecard.csv")
    nav   = pd.read_csv(PROCESSED / "clean_nav_history.csv", parse_dates=["date"])
    fm    = pd.read_csv(PROCESSED / "clean_fund_master.csv")
    sip   = pd.read_csv(PROCESSED / "clean_monthly_sip_inflows.csv", parse_dates=["month"])
    var   = pd.read_csv(PROCESSED / "var_cvar_report.csv")
    return score, nav, fm, sip, var


def compute_weekly_returns(nav: pd.DataFrame, top_codes: list) -> pd.DataFrame:
    """Compute last 7-day return for top funds."""
    results = []
    for code in top_codes:
        grp = nav[nav["amfi_code"] == code].sort_values("date")
        if len(grp) < 8:
            continue
        last_nav = grp["nav"].iloc[-1]
        week_ago = grp["nav"].iloc[-6] if len(grp) >= 6 else grp["nav"].iloc[0]
        weekly_ret = (last_nav / week_ago - 1) * 100
        results.append({"amfi_code": code, "last_nav": last_nav, "weekly_return": weekly_ret})
    return pd.DataFrame(results)


def color_for_value(val: float, good_positive=True) -> str:
    if good_positive:
        return "#16a34a" if val > 0 else "#dc2626"
    else:
        return "#dc2626" if val > -1 else "#16a34a"


def generate_html(score, nav, fm, sip, var) -> str:
    today       = datetime.now().strftime("%d %B %Y")
    top5_codes  = score.head(5)["amfi_code"].tolist()
    weekly      = compute_weekly_returns(nav, top5_codes)
    merged      = score.head(5).copy()
    merged      = merged.merge(weekly, on="amfi_code", how="left")

    latest_sip  = sip.sort_values("month").iloc[-1]
    top_var     = var.sort_values("var_95_pct").iloc[0]
    safest      = var.sort_values("var_95_pct", ascending=False).iloc[0]

    # Build top funds rows
    fund_rows = ""
    for _, r in merged.iterrows():
        wr   = r.get("weekly_return", 0)
        wcol = color_for_value(wr)
        fund_rows += f"""
        <tr>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; font-weight:600; color:#1e2761;">{r['fund_house'].replace(' Mutual Fund','')}</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; color:#64748b;">{r['sub_category']}</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; text-align:right;">₹{r['last_nav']:,.2f}</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; text-align:right; color:{wcol}; font-weight:600;">{wr:+.2f}%</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; text-align:right;">{r['cagr_3yr']}%</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; text-align:right;">{r['sharpe']}</td>
          <td style="padding:10px 14px; border-bottom:1px solid #e2e8f0; text-align:right; font-weight:700; color:#1e2761;">{r['score']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bluestock MF Weekly Report — {today}</title>
</head>
<body style="margin:0; padding:0; background:#f0f4ff; font-family: Arial, sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4ff; padding:30px 0;">
<tr><td align="center">
<table width="680" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 4px 24px rgba(30,39,97,0.10);">

  <!-- Header -->
  <tr>
    <td style="background:#1e2761; padding:32px 36px;">
      <table width="100%"><tr>
        <td>
          <div style="color:#cadcfc; font-size:12px; letter-spacing:3px; text-transform:uppercase; margin-bottom:6px;">BLUESTOCK FINTECH</div>
          <div style="color:#ffffff; font-size:26px; font-weight:700;">Weekly MF Performance Report</div>
          <div style="color:#cadcfc; font-size:14px; margin-top:6px;">{today}</div>
        </td>
        <td align="right">
          <div style="background:rgba(255,255,255,0.1); border-radius:8px; padding:12px 18px; text-align:center;">
            <div style="color:#f59e0b; font-size:22px; font-weight:700;">₹81L Cr</div>
            <div style="color:#cadcfc; font-size:11px;">Industry AUM</div>
          </div>
        </td>
      </tr></table>
    </td>
  </tr>

  <!-- KPI Cards -->
  <tr>
    <td style="padding:24px 36px 0;">
      <table width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td width="25%" style="padding-right:12px;">
          <div style="background:#f4f7ff; border-radius:8px; padding:16px; text-align:center;">
            <div style="color:#1e2761; font-size:22px; font-weight:700;">₹{latest_sip['sip_inflow_crore']:,.0f} Cr</div>
            <div style="color:#64748b; font-size:11px; margin-top:4px;">Latest SIP Inflow</div>
          </div>
        </td>
        <td width="25%" style="padding-right:12px;">
          <div style="background:#f4f7ff; border-radius:8px; padding:16px; text-align:center;">
            <div style="color:#1e2761; font-size:22px; font-weight:700;">{latest_sip['active_sip_accounts_crore']:.2f} Cr</div>
            <div style="color:#64748b; font-size:11px; margin-top:4px;">Active SIP Accounts</div>
          </div>
        </td>
        <td width="25%" style="padding-right:12px;">
          <div style="background:#fff4e5; border-radius:8px; padding:16px; text-align:center;">
            <div style="color:#b45309; font-size:22px; font-weight:700;">{top_var['var_95_pct']:.2f}%</div>
            <div style="color:#64748b; font-size:11px; margin-top:4px;">Highest VaR (95%)</div>
          </div>
        </td>
        <td width="25%">
          <div style="background:#f0fdf4; border-radius:8px; padding:16px; text-align:center;">
            <div style="color:#15803d; font-size:22px; font-weight:700;">{safest['var_95_pct']:.2f}%</div>
            <div style="color:#64748b; font-size:11px; margin-top:4px;">Lowest VaR (Safest)</div>
          </div>
        </td>
      </tr>
      </table>
    </td>
  </tr>

  <!-- Top Funds Table -->
  <tr>
    <td style="padding:24px 36px 0;">
      <div style="font-size:16px; font-weight:700; color:#1e2761; margin-bottom:12px;">Top 5 Funds by Scorecard</div>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
        <thead>
          <tr style="background:#1e2761;">
            <th style="padding:10px 14px; text-align:left; color:#ffffff; font-size:12px;">Fund</th>
            <th style="padding:10px 14px; text-align:left; color:#ffffff; font-size:12px;">Category</th>
            <th style="padding:10px 14px; text-align:right; color:#ffffff; font-size:12px;">NAV</th>
            <th style="padding:10px 14px; text-align:right; color:#ffffff; font-size:12px;">7-Day Ret</th>
            <th style="padding:10px 14px; text-align:right; color:#ffffff; font-size:12px;">3yr CAGR</th>
            <th style="padding:10px 14px; text-align:right; color:#ffffff; font-size:12px;">Sharpe</th>
            <th style="padding:10px 14px; text-align:right; color:#ffffff; font-size:12px;">Score</th>
          </tr>
        </thead>
        <tbody>{fund_rows}</tbody>
      </table>
    </td>
  </tr>

  <!-- Insights -->
  <tr>
    <td style="padding:24px 36px 0;">
      <div style="font-size:16px; font-weight:700; color:#1e2761; margin-bottom:12px;">Key Insights This Week</div>
      <table width="100%" cellpadding="0" cellspacing="0">
        {"".join([f'''<tr><td style="padding:8px 0; border-bottom:1px solid #f0f4ff;">
          <span style="display:inline-block; background:#1e2761; color:#fff; border-radius:50%; width:22px; height:22px; text-align:center; line-height:22px; font-size:11px; font-weight:700; margin-right:10px;">{i+1}</span>
          <span style="color:#334155; font-size:13px;">{insight}</span>
        </td></tr>''' for i, insight in enumerate([
            f"ICICI Pru Mid Cap leads with score 84.5 — 3yr CAGR {score.iloc[0]['cagr_3yr']}%, Sharpe {score.iloc[0]['sharpe']}",
            f"Industry SIP inflow at ₹{latest_sip['sip_inflow_crore']:,.0f} Cr with {latest_sip['active_sip_accounts_crore']:.2f} crore active accounts",
            f"Highest risk fund: {top_var['fund_house']} — daily VaR {top_var['var_95_pct']:.2f}% at 95% confidence",
            f"Monte Carlo projects ICICI Pru Mid Cap median NAV of ₹1,822 in 5 years (30.9% CAGR)",
            "97.8% of investors have SIP gaps > 35 days — churn risk remains high across AMCs",
        ])])}
      </table>
    </td>
  </tr>

  <!-- Footer -->
  <tr>
    <td style="padding:24px 36px 32px;">
      <div style="background:#f4f7ff; border-radius:8px; padding:16px; text-align:center;">
        <div style="color:#64748b; font-size:12px;">Generated by Bluestock MF Analytics Platform | Soham Joshi | June 2026</div>
        <div style="color:#64748b; font-size:11px; margin-top:4px;">Data: AMFI India | mfapi.in | NSE | For educational purposes only. Not financial advice.</div>
        <div style="margin-top:10px;">
          <a href="https://github.com/Physics0070/capstone-project" style="color:#1e2761; font-size:12px; font-weight:600;">github.com/Physics0070/capstone-project</a>
        </div>
      </div>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""
    return html


def send_email(html: str, recipient: str, sender: str, password: str):
    """Send HTML email via Gmail SMTP. Configure credentials before use."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Bluestock MF Weekly Report — {datetime.now().strftime('%d %b %Y')}"
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print(f"  ✓ Email sent to {recipient}")
    except Exception as e:
        print(f"  ✗ Email failed: {e}")
        print(f"    To send manually: open reports/weekly_performance_report.html in a browser")


if __name__ == "__main__":
    print(f"\n{'='*55}")
    print("  EMAIL REPORT GENERATOR — Bonus B5")
    print(f"{'='*55}\n")

    score, nav, fm, sip, var = load_data()
    html = generate_html(score, nav, fm, sip, var)

    # Save HTML report
    report_path = REPORTS / "weekly_performance_report.html"
    report_path.write_text(html, encoding="utf-8")
    print(f"  ✓ weekly_performance_report.html saved to reports/")
    print(f"    Open in browser to preview the email")

    # ── TO SEND VIA EMAIL ──────────────────────────────────────────────────────
    # Uncomment and fill in credentials to send:
    #
    # SENDER    = "your_gmail@gmail.com"
    # PASSWORD  = "your_app_password"   # Gmail App Password (not your login password)
    # RECIPIENT = "recipient@email.com"
    # send_email(html, RECIPIENT, SENDER, PASSWORD)
    # ──────────────────────────────────────────────────────────────────────────

    print(f"\n{'='*55}")
    print("  Bonus B5 — Email Report Generator Complete")
    print(f"{'='*55}\n")
