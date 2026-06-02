-- queries.sql
-- Bluestock Fintech Capstone — 10 Analytical Queries

-- Q1: Top 5 funds by AUM
SELECT scheme_name, fund_house, category, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Q2: Average NAV per month for each fund (last 12 months)
SELECT amfi_code,
       strftime('%Y-%m', date) AS month,
       ROUND(AVG(nav), 4)      AS avg_nav
FROM fact_nav
WHERE date >= date('now', '-12 months')
GROUP BY amfi_code, month
ORDER BY amfi_code, month;

-- Q3: SIP inflow YoY growth
SELECT strftime('%Y', month) AS year,
       SUM(sip_inflow_crore)  AS total_sip_inflow_crore
FROM fact_sip_industry
GROUP BY year
ORDER BY year;

-- Q4: Total transaction amount by state
SELECT state,
       COUNT(*)              AS num_transactions,
       SUM(amount_inr)       AS total_amount_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_inr DESC;

-- Q5: Funds with expense ratio below 1%
SELECT f.scheme_name, f.fund_house, f.category, f.expense_ratio_pct
FROM dim_fund f
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct;

-- Q6: Top 5 funds by Sharpe ratio
SELECT scheme_name, fund_house, sharpe_ratio, return_3yr_pct, risk_grade
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 5;

-- Q7: SIP vs Lumpsum vs Redemption split
SELECT transaction_type,
       COUNT(*)        AS count,
       SUM(amount_inr) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- Q8: Average SIP amount by age group
SELECT age_group,
       COUNT(*)             AS num_sips,
       ROUND(AVG(amount_inr), 0) AS avg_sip_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY age_group
ORDER BY age_group;

-- Q9: AUM growth by fund house (latest vs earliest quarter)
SELECT fund_house,
       MIN(aum_crore) AS aum_start,
       MAX(aum_crore) AS aum_end,
       ROUND((MAX(aum_crore) - MIN(aum_crore)) * 100.0 / MIN(aum_crore), 2) AS growth_pct
FROM fact_aum
GROUP BY fund_house
ORDER BY growth_pct DESC;

-- Q10: Top 5 sectors by total portfolio weight across all funds
SELECT sector,
       COUNT(DISTINCT amfi_code)   AS num_funds,
       ROUND(AVG(weight_pct), 2)   AS avg_weight_pct,
       ROUND(SUM(weight_pct), 2)   AS total_weight_pct
FROM fact_portfolio
GROUP BY sector
ORDER BY total_weight_pct DESC
LIMIT 5;
