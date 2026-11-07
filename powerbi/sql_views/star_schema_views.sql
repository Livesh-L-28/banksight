-- ==============================================================================
-- BankSight Power BI Semantic Layer: Star Schema Views
-- Fact and Dimension views for enterprise Business Intelligence modeling
-- ==============================================================================

-- 1. DimDate: Standard Gregorian calendar dimension
CREATE VIEW IF NOT EXISTS DimDate AS
WITH RECURSIVE DateRange(dt) AS (
    SELECT '2020-01-01'
    UNION ALL
    SELECT date(dt, '+1 day')
    FROM DateRange
    WHERE dt < '2026-12-31'
)
SELECT 
    dt AS DateKey,
    strftime('%Y', dt) AS Year,
    strftime('%m', dt) AS Month,
    strftime('%Y-%m', dt) AS YearMonth,
    strftime('%d', dt) AS DayOfMonth,
    CASE strftime('%w', dt)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        ELSE 'Saturday'
    END AS DayOfWeek,
    CASE 
        WHEN strftime('%m', dt) IN ('01', '02', '03') THEN 'Q1'
        WHEN strftime('%m', dt) IN ('04', '05', '06') THEN 'Q2'
        WHEN strftime('%m', dt) IN ('07', '08', '09') THEN 'Q3'
        ELSE 'Q4'
    END AS Quarter,
    CASE WHEN strftime('%w', dt) IN ('0', '6') THEN 1 ELSE 0 END AS IsWeekend
FROM DateRange;


-- 2. DimBranch: Branch geographical dimension
CREATE VIEW IF NOT EXISTS DimBranch AS
SELECT 
    branch_id AS BranchKey,
    branch_name AS BranchName,
    branch_code AS BranchCode,
    city AS City,
    state AS State,
    region AS Region,
    postal_code AS PostalCode,
    is_active AS IsActive
FROM branches;


-- 3. DimProduct: Banking product catalog dimension
CREATE VIEW IF NOT EXISTS DimProduct AS
SELECT 
    product_id AS ProductKey,
    product_code AS ProductCode,
    product_name AS ProductName,
    category AS ProductCategory,
    annual_fee AS AnnualFee,
    interest_rate_pct AS InterestRatePct,
    target_segment AS TargetSegment,
    is_active AS IsActive
FROM products;


-- 4. DimCustomer: Customer demographic and profile dimension
CREATE VIEW IF NOT EXISTS DimCustomer AS
SELECT 
    c.customer_id AS CustomerKey,
    c.first_name || ' ' || c.last_name AS CustomerName,
    c.email AS Email,
    c.age AS Age,
    c.gender AS Gender,
    c.occupation AS Occupation,
    c.annual_income AS AnnualIncome,
    c.city AS City,
    c.state AS State,
    c.branch_id AS BranchKey,
    c.joining_date AS JoiningDate,
    c.customer_tenure_months AS CustomerTenureMonths,
    c.customer_status AS CustomerStatus,
    c.customer_segment AS CustomerSegment,
    c.credit_score AS CreditScore,
    c.digital_banking_active AS DigitalBankingActive,
    c.mobile_banking_active AS MobileBankingActive,
    c.churn_flag AS ChurnFlag
FROM customers c;


-- 5. DimAccount: Banking account dimension
CREATE VIEW IF NOT EXISTS DimAccount AS
SELECT 
    a.account_id AS AccountKey,
    a.account_number AS AccountNumber,
    a.customer_id AS CustomerKey,
    a.branch_id AS BranchKey,
    act.type_name AS AccountTypeName,
    act.category AS AccountCategory,
    a.currency AS Currency,
    a.account_status AS AccountStatus,
    a.open_date AS OpenDate,
    a.is_primary AS IsPrimary
FROM accounts a
JOIN account_types act ON a.type_id = act.type_id;


-- 6. FactTransactions: Transactional line fact table
CREATE VIEW IF NOT EXISTS FactTransactions AS
SELECT 
    t.transaction_id AS TransactionKey,
    date(t.transaction_date) AS DateKey,
    t.account_id AS AccountKey,
    t.customer_id AS CustomerKey,
    t.branch_id AS BranchKey,
    t.transaction_type AS TransactionType,
    t.channel AS Channel,
    t.amount AS TransactionAmount,
    t.balance_after AS BalanceAfter,
    t.status AS TransactionStatus,
    t.merchant_category AS MerchantCategory
FROM transactions t;


-- 7. FactCustomerSnapshot: Monthly customer balance, RFM, and churn risk snapshot
CREATE VIEW IF NOT EXISTS FactCustomerSnapshot AS
SELECT 
    c.customer_id AS CustomerKey,
    c.branch_id AS BranchKey,
    COALESCE(SUM(a.current_balance), 0.0) AS TotalDepositBalance,
    COUNT(a.account_id) AS OpenAccountCount,
    COALESCE(cp.churn_probability, 0.15) AS ChurnProbability,
    COALESCE(cp.risk_category, 'Low Risk') AS RiskCategory,
    c.churn_flag AS IsChurned
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN churn_predictions cp ON c.customer_id = cp.customer_id
GROUP BY c.customer_id, c.branch_id, cp.churn_probability, cp.risk_category, c.churn_flag;


-- 8. FactCampaign: Campaign assignment and response fact table
CREATE VIEW IF NOT EXISTS FactCampaign AS
SELECT 
    ca.assignment_id AS CampaignAssignmentKey,
    ca.campaign_id AS CampaignKey,
    ca.customer_id AS CustomerKey,
    ca.assigned_date AS AssignedDateKey,
    ca.contacted AS IsContacted,
    COALESCE(cr.responded, 0) AS IsResponded,
    COALESCE(cr.converted, 0) AS IsConverted,
    COALESCE(cr.attributed_revenue, 0.0) AS AttributedRevenue
FROM campaign_assignments ca
LEFT JOIN campaign_responses cr ON ca.assignment_id = cr.assignment_id;


-- 9. FactRetention: Operational retention case and outcome fact table
CREATE VIEW IF NOT EXISTS FactRetention AS
SELECT 
    rc.case_id AS RetentionCaseKey,
    rc.customer_id AS CustomerKey,
    rc.rm_id AS RelationshipManagerKey,
    date(rc.created_at) AS CreatedDateKey,
    rc.status AS RetentionStatus,
    rc.risk_level AS RiskLevel,
    rc.churn_probability AS ChurnProbability,
    CASE WHEN rc.status = 'Retained' THEN 1 ELSE 0 END AS IsRetained,
    CASE WHEN rc.status = 'Not Retained' THEN 1 ELSE 0 END AS IsLost
FROM retention_cases rc;
