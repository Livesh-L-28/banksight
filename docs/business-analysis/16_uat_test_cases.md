# User Acceptance Testing (UAT) Test Cases
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. UAT Execution Test Suite

### UAT-01: Executive Dashboard Dynamic Slicing
- **Test ID:** `UAT-EX-01`
- **User Role:** Head of Retail Banking
- **Description:** Verify that selecting a specific Branch (e.g., "Downtown Central Branch") recalculates all dashboard KPIs and updates charts without error.
- **Pre-Conditions:** Database populated with branch and transaction data.
- **Steps:**
  1. Navigate to Executive Dashboard.
  2. Select "Downtown Central Branch" in Branch filter.
  3. Change Date Range to "Last 6 Months".
- **Expected Result:**
  - KPI cards refresh to reflect Downtown Central Branch totals.
  - Drill-down customer table updates to customers belonging only to that branch.
  - Total deposits and active customer counts match database queries.
- **Status:** PASS

### UAT-02: Customer 360 Full Dossier & Search
- **Test ID:** `UAT-C360-01`
- **User Role:** Relationship Manager
- **Description:** Search for customer "CUST-00001" and review their multi-account holdings and chronological timeline.
- **Steps:**
  1. Navigate to Customer 360 page.
  2. Enter "CUST-00001" in search bar.
  3. Select customer from results.
  4. Inspect Accounts tab, Timeline tab, and Risk tab.
- **Expected Result:**
  - Displays customer name, age, income, tenure, assigned branch, and current churn score.
  - Accounts tab displays checking and savings account balances.
  - Activity timeline renders transactions and complaints in chronological order.
- **Status:** PASS

### UAT-03: Machine Learning Model Benchmarking & Calibrated Churn Scoring
- **Test ID:** `UAT-ML-01`
- **User Role:** Banking Data Analyst
- **Description:** Execute model training across Logistic Regression, Random Forest, and Gradient Boosting; inspect metric evaluation table.
- **Steps:**
  1. Navigate to Model Management / Churn Intelligence page.
  2. Trigger Model Benchmark training.
  3. Verify ROC-AUC and PR-AUC curves.
- **Expected Result:**
  - System executes training without data leakage.
  - Displays metrics table with Accuracy, Precision, Recall, F1, ROC-AUC.
  - Gradient Boosting / Random Forest achieves ROC-AUC $\ge 0.80$.
  - Displays top contributing features (e.g., balance drop, complaint frequency).
- **Status:** PASS

### UAT-04: Retention Workflow Case Progression & Audit Persistence
- **Test ID:** `UAT-RET-01`
- **User Role:** Retention Manager
- **Description:** Open a retention case for a high-risk customer, update status through lifecycle, and verify database persistence.
- **Steps:**
  1. Navigate to Retention Management page.
  2. Locate a customer in the High Risk queue.
  3. Click "Create Retention Case", assign to RM "Sarah Jenkins", select follow-up date.
  4. Update status from `Identified` to `Contacted`, add note: "Client satisfied with waiver offer."
  5. Update status to `Retained`.
  6. Refresh page and verify case persists in database.
- **Expected Result:**
  - Case status updates immediately.
  - Action log displays timestamp, user action, and notes.
  - Database row in `retention_cases` shows `status = 'Retained'`.
- **Status:** PASS

### UAT-05: Multi-Format Report Export
- **Test ID:** `UAT-REP-01`
- **User Role:** Business Analyst
- **Description:** Generate and export the Executive Banking Performance Report in Excel and CSV formats.
- **Steps:**
  1. Navigate to Reports page.
  2. Select "Executive Banking Performance Report".
  3. Click "Download Excel (.xlsx)".
  4. Click "Download CSV (.csv)".
- **Expected Result:**
  - Files download successfully without corruption.
  - Excel contains formatted summary headers, KPI table, and executive recommendations.
- **Status:** PASS
