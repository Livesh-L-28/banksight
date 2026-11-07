# Acceptance Criteria Specification
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Acceptance Criteria by Feature Module (Given-When-Then Format)

### Module 1: Executive Dashboard
- **AC-EX-01 Dynamic Metric Recalculation:**
  - *Given* an authenticated user on the Executive Dashboard,
  - *When* the user adjusts the Date Range, Branch filter, or Segment filter,
  - *Then* all KPI cards (Total Customers, Active Customers, Deposits, Churn Rate, Retention Rate, ARPU, CLV) must recalculate dynamically within 1.5 seconds without hardcoded default values.
- **AC-EX-02 Trend Visualizations:**
  - *Given* the Executive Dashboard is rendered,
  - *When* viewing the monthly transaction and deposit/withdrawal trends,
  - *Then* interactive Plotly charts must display real aggregated figures with hover details and matching totals in the summary cards.

### Module 2: Customer 360 Dossier
- **AC-C360-01 Customer Search & Filter:**
  - *Given* the Customer 360 search view,
  - *When* the user inputs a Customer ID or name substring (e.g. "Smith" or "CUST-00102"),
  - *Then* the matching customer records must be returned with demographic attributes, branch assignment, and account preview.
- **AC-C360-02 Complete Customer Dossier:**
  - *Given* a selected customer profile,
  - *When* viewing the profile tabs,
  - *Then* the user can view account balances, transaction history, loan/credit card products, complaints history, and chronological timeline.

### Module 3: Customer Segmentation
- **AC-SEG-01 RFM Quintile Assignment:**
  - *Given* a populated transaction ledger,
  - *When* the RFM analysis pipeline runs,
  - *Then* every active customer must be assigned a Recency score (1-5), Frequency score (1-5), Monetary score (1-5), and a composite segment label (e.g. "High Value", "Loyal", "At Risk", "Dormant").
- **AC-SEG-02 K-Means Clustering & Profiling:**
  - *Given* normalized customer behavioral and financial vectors,
  - *When* K-Means clustering is executed with $k \in [3, 8]$,
  - *Then* cluster centroids must be computed, silhouette score reported, and empirical business labels assigned based on measured feature values (never raw cluster numbers alone).

### Module 4: Churn Intelligence & ML
- **AC-ML-01 Multi-Model Benchmarking:**
  - *Given* the model training interface with train/test separation (80/20) and stratified splits,
  - *When* model training is triggered,
  - *Then* Logistic Regression, Random Forest, and Gradient Boosting must be trained, displaying side-by-side Accuracy, Precision, Recall, F1, and ROC-AUC.
- **AC-ML-02 Calibrated Risk Categories:**
  - *Given* a scored customer cohort,
  - *When* churn probability is computed,
  - *Then* customers with $P(\text{churn}) > 0.65$ are categorized as `High Risk`, $0.35 \le P(\text{churn}) \le 0.65$ as `Medium Risk`, and $< 0.35$ as `Low Risk`.
- **AC-ML-03 Explainable AI Attribution:**
  - *Given* a high-risk customer profile,
  - *When* churn explanation is inspected,
  - *Then* the system must display the top 3 contributing factors (e.g. "Recent complaint unaddressed", "Deposit balance declined >30%", "Low digital engagement").

### Module 5: Operational Retention Case Management
- **AC-RET-01 Case Creation & DB Persistence:**
  - *Given* a customer identified as high churn risk,
  - *When* a retention case is opened, assigned to an RM, and saved,
  - *Then* a new row must be persisted in the `retention_cases` database table with status `Identified` or `Assigned`.
- **AC-RET-02 Workflow Status Progression:**
  - *Given* an active retention case,
  - *When* the RM updates status to `Contacted`, `Offer Proposed`, or `Retained`,
  - *Then* the database must update the case record, record an audit entry in `retention_actions`, and reflect the updated count in the retention funnel.

### Module 6: Transaction Analytics & Reconciliation
- **AC-TXN-01 Analytical Reconciliation Checks:**
  - *Given* the transaction analytics module,
  - *When* reconciliation audit is run,
  - *Then* system displays total record count, total deposit value, total withdrawal value, flagged duplicate transaction IDs (if any), and dormant account counts (>90 days inactive).

### Module 7: Campaign Intelligence & Attribution
- **AC-CMP-01 Attribution & ROI Computation:**
  - *Given* a completed campaign record,
  - *When* performance metrics are calculated,
  - *Then* Reach, Response Rate, Conversion Rate, Marketing Cost, Attributed Revenue, and net ROI must be displayed with transparent formula notation.

### Module 8 & 9: Branch & Product Intelligence
- **AC-BRN-01 Branch Ranking & Benchmarking:**
  - *Given* the Branch Analytics view,
  - *When* branch metrics are aggregated,
  - *Then* branches are ranked by Total Deposits, Customer Growth, and Attrition Rate, highlighting underperforming outliers.
- **AC-PRD-01 Transparent Cross-Sell Recommendation:**
  - *Given* an existing checking account customer with >$15,000 balance and no term deposit,
  - *When* product intelligence is evaluated,
  - *Then* system surfaces a "Term / Fixed Deposit" recommendation with advisory tag.

### Module 10: Business Reporting
- **AC-REP-01 Report Generation & Export:**
  - *Given* any of the 8 standard reports (Executive, Segmentation, Churn, Retention, Campaign, Branch, Product, Behavior),
  - *When* the user requests an export in CSV, Excel, or PDF,
  - *Then* a valid, non-corrupt file is generated and downloaded containing header metadata, active filters, KPI table, and executive business recommendations.

