-- ==============================================================================
-- BankSight Sample Analytical SQL Queries
-- Purpose: Standard analytical query library for core banking KPIs, RFM, Churn & Branching
-- Target Database: PostgreSQL 16+ / SQLite (Dialect Agnostic ANSI-SQL)
-- ==============================================================================

-- 1. Executive Portfolio Balance & Customer Health Summary
SELECT 
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT CASE WHEN c.customer_status = 'Active' THEN c.customer_id END) AS active_customers,
    COUNT(DISTINCT CASE WHEN c.churn_flag = 1 THEN c.customer_id END) AS churned_customers,
    ROUND(CAST(COUNT(DISTINCT CASE WHEN c.churn_flag = 1 THEN c.customer_id END) AS FLOAT) / 
          NULLIF(COUNT(DISTINCT c.customer_id), 0) * 100, 2) AS churn_rate_pct,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    ROUND(SUM(a.current_balance), 2) AS total_portfolio_balance,
    ROUND(AVG(a.current_balance), 2) AS avg_account_balance
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id;


-- 2. Monthly Deposit vs Withdrawal Volume Trend
SELECT 
    strftime('%Y-%m', transaction_date) AS txn_month,
    SUM(CASE WHEN transaction_type = 'Deposit' THEN amount ELSE 0 END) AS total_deposits,
    SUM(CASE WHEN transaction_type = 'Withdrawal' THEN amount ELSE 0 END) AS total_withdrawals,
    SUM(CASE WHEN transaction_type = 'Deposit' THEN amount ELSE -amount END) AS net_cashflow,
    COUNT(transaction_id) AS total_transaction_count
FROM transactions
WHERE status = 'Completed'
GROUP BY strftime('%Y-%m', transaction_date)
ORDER BY txn_month DESC;


-- 3. Branch Performance Ranking (Deposits, Customers, and Churn Rate)
SELECT 
    b.branch_id,
    b.branch_name,
    b.region,
    COUNT(DISTINCT c.customer_id) AS branch_customer_count,
    ROUND(SUM(a.current_balance), 2) AS total_branch_deposits,
    ROUND(AVG(a.current_balance), 2) AS avg_customer_balance,
    ROUND(CAST(SUM(CASE WHEN c.churn_flag = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
          NULLIF(COUNT(c.customer_id), 0) * 100, 2) AS branch_churn_rate_pct
FROM branches b
LEFT JOIN customers c ON b.branch_id = c.branch_id
LEFT JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY b.branch_id, b.branch_name, b.region
ORDER BY total_branch_deposits DESC;


-- 4. RFM (Recency, Frequency, Monetary) Customer Raw Scoring
WITH CustomerTxnAgg AS (
    SELECT 
        customer_id,
        MAX(transaction_date) AS last_txn_date,
        COUNT(transaction_id) AS txn_count_12m,
        SUM(amount) AS total_spend_12m
    FROM transactions
    WHERE status = 'Completed'
    GROUP BY customer_id
)
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.customer_segment,
    COALESCE(cta.txn_count_12m, 0) AS frequency,
    COALESCE(cta.total_spend_12m, 0.0) AS monetary,
    COALESCE(cta.last_txn_date, 'None') AS last_active_date
FROM customers c
LEFT JOIN CustomerTxnAgg cta ON c.customer_id = cta.customer_id
ORDER BY monetary DESC
LIMIT 50;


-- 5. Operational Retention Queue: High Risk Customers with Churn Probability
SELECT 
    rc.case_id,
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    b.branch_name,
    rm.first_name || ' ' || rm.last_name AS relationship_manager,
    rc.churn_probability,
    rc.risk_level,
    rc.status AS case_status,
    rc.proposed_offer,
    rc.follow_up_date
FROM retention_cases rc
JOIN customers c ON rc.customer_id = c.customer_id
JOIN branches b ON c.branch_id = b.branch_id
LEFT JOIN relationship_managers rm ON rc.rm_id = rm.rm_id
WHERE rc.status IN ('Identified', 'Assigned', 'Contacted')
ORDER BY rc.churn_probability DESC;
