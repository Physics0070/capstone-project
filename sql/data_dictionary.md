# Data Dictionary — Bluestock MF Capstone

## 01_fund_master.csv / dim_fund
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | AMFI unique scheme code (PK) |
| fund_house | TEXT | AMC name |
| scheme_name | TEXT | Full AMFI scheme name |
| category | TEXT | Equity / Debt |
| sub_category | TEXT | Large Cap / Mid Cap / Small Cap etc. |
| plan | TEXT | Regular or Direct |
| launch_date | DATE | Fund launch date |
| benchmark | TEXT | Official benchmark index |
| expense_ratio_pct | REAL | Annual expense ratio % |
| exit_load_pct | REAL | Exit load % |
| min_sip_amount | INTEGER | Minimum SIP amount in Rs. |
| min_lumpsum_amount | INTEGER | Minimum lumpsum in Rs. |
| fund_manager | TEXT | Primary fund manager name |
| risk_category | TEXT | Low / Moderate / High / Very High |
| sebi_category_code | TEXT | SEBI internal category code |

## 02_nav_history.csv / fact_nav
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | FK to dim_fund |
| date | DATE | NAV date (business days, forward-filled) |
| nav | REAL | NAV in Rs. |
| daily_return | REAL | nav_t/nav_t-1 - 1 (computed during load) |

## 03_aum_by_fund_house.csv / fact_aum
| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Quarter end date |
| fund_house | TEXT | AMC name |
| aum_lakh_crore | REAL | AUM in Rs. lakh crore |
| aum_crore | INTEGER | AUM in Rs. crore |
| num_schemes | INTEGER | Number of schemes |

## 04_monthly_sip_inflows.csv / fact_sip_industry
| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Month (YYYY-MM-DD) |
| sip_inflow_crore | INTEGER | SIP inflows in Rs. crore |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore |
| new_sip_accounts_lakh | REAL | New SIP registrations in lakh |
| sip_aum_lakh_crore | REAL | SIP AUM in Rs. lakh crore |
| yoy_growth_pct | REAL | YoY growth % (0 for first 12 months) |

## 05_category_inflows.csv
| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Month |
| category | TEXT | Fund category |
| net_inflow_crore | REAL | Net inflow in Rs. crore |

## 06_industry_folio_count.csv
| Column | Type | Description |
|--------|------|-------------|
| month | DATE | Month |
| total_folios_crore | REAL | Total folios in crore |
| equity_folios_crore | REAL | Equity folios in crore |
| debt_folios_crore | REAL | Debt folios in crore |
| hybrid_folios_crore | REAL | Hybrid folios in crore |
| others_folios_crore | REAL | Others folios in crore |

## 07_scheme_performance.csv / fact_performance
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | FK to dim_fund |
| return_1yr_pct | REAL | 1-year return % |
| return_3yr_pct | REAL | 3-year CAGR % |
| return_5yr_pct | REAL | 5-year CAGR % |
| benchmark_3yr_pct | REAL | Benchmark 3yr CAGR % |
| alpha | REAL | Excess return over benchmark |
| beta | REAL | Market sensitivity |
| sharpe_ratio | REAL | Risk-adjusted return |
| sortino_ratio | REAL | Downside risk-adjusted return |
| std_dev_ann_pct | REAL | Annualised standard deviation % |
| max_drawdown_pct | REAL | Worst peak-to-trough decline |
| aum_crore | INTEGER | AUM in Rs. crore |
| morningstar_rating | INTEGER | 1-5 star rating |
| risk_grade | TEXT | Risk classification |

## 08_investor_transactions.csv / fact_transactions
| Column | Type | Description |
|--------|------|-------------|
| investor_id | TEXT | Unique investor ID |
| transaction_date | DATE | Date of transaction |
| amfi_code | INTEGER | FK to dim_fund |
| transaction_type | TEXT | Sip / Lumpsum / Redemption |
| amount_inr | INTEGER | Transaction amount in Rs. |
| state | TEXT | Investor state |
| city | TEXT | Investor city |
| city_tier | TEXT | T30 or B30 |
| age_group | TEXT | 18-25 / 26-35 / 36-45 / 46-55 / 56+ |
| gender | TEXT | Male / Female |
| annual_income_lakh | REAL | Annual income in Rs. lakh |
| payment_mode | TEXT | UPI / Net Banking / Mandate / Cheque |
| kyc_status | TEXT | Verified / Pending |

## 09_portfolio_holdings.csv / fact_portfolio
| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | FK to dim_fund |
| stock_symbol | TEXT | NSE stock symbol |
| stock_name | TEXT | Company name |
| sector | TEXT | Industry sector |
| weight_pct | REAL | Portfolio weight % |
| market_value_cr | REAL | Market value in Rs. crore |
| current_price_inr | REAL | Stock price in Rs. |
| portfolio_date | DATE | Holdings as-of date |

## 10_benchmark_indices.csv
| Column | Type | Description |
|--------|------|-------------|
| date | DATE | Trading date |
| index_name | TEXT | NIFTY50 / NIFTY100 / BSESmallCap etc. |
| close_value | REAL | Index closing value |
