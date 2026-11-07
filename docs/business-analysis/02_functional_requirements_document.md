# Functional Requirements Document (FRD)
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. System Overview
The BankSight platform is structured into modular functional components interacting via a clean service and repository pattern over a relational database, an analytics computation layer, and an interactive Streamlit user interface.

## 2. Functional Module Breakdown

### FR-01: Executive Intelligence Dashboard
- **FR-01.1 Dynamic KPI Calculation:** Compute Total Customers, Active Customers, Inactive Customers, New Additions, Total Accounts, Deposit Volume, Withdrawal Volume, Net Balance, Average Balance, ARPU, Churn Rate, Retention Rate, CLV, High-Risk Count, and Conversion Rate dynamically based on active filters.
- **FR-01.2 Multidimensional Slicers:** Provide interactive filtering across Date Range, Branch Locations, Customer Segments, and Banking Product Types without full-page reloads.
- **FR-01.3 Drill-Down Capability:** Enable users to click on visual KPI cards or charts to inspect underlying customer or transactional cohorts.
- **FR-01.4 Data Export:** Provide one-click data extraction of filtered views into CSV and Excel formats.

### FR-02: Customer 360 Intelligence Profile
- **FR-02.1 Unified Customer Search:** Search by Customer ID, Full Name, City, or Account Number with instant autocomplete and matching.
- **FR-02.2 Comprehensive Dossier:** Display demographic attributes (Age, Gender, Occupation, Income, Location, Tenure), account portfolio (Checking, Savings, Deposits, Loans, Credit Cards), and historical balance metrics.
- **FR-02.3 Behavioral Timeline:** Visual chronology of interactions, complaints, digital logins, and transactions over the past 12-24 months.
- **FR-02.4 Risk & Segment Classification:** Prominently display current RFM segment, K-Means cluster assignment, churn risk tier, and assigned Relationship Manager.

### FR-03: Customer Segmentation Engine
- **FR-03.1 Multi-Criteria Segmentation:** Support Demographic (age/income brackets), Geographic (state/city/branch), Behavioral (digital vs in-branch usage), and Financial (balance tiers).
- **FR-03.2 RFM Segmentation Pipeline:** Compute Recency (days since last activity), Frequency (transaction count in past 12 months), and Monetary Value (total transaction / average balance) quantiles with scores 1 to 5.
- **FR-03.3 K-Means Clustering:** Implement unsupervised clustering on normalized customer features with configurable cluster counts (k=3 to 8), automated silhouette/elbow assessment, and measured characteristic labeling (e.g. "High Value Wealth", "Digital Young Active", "Dormant Traditional").
- **FR-03.4 Actionable Playbooks:** Generate business recommendations tailored to each identified segment.

### FR-04: Customer Churn Intelligence & Machine Learning
- **FR-04.1 ML Pipeline:** Automated feature extraction without future data leakage, handling class imbalance via SMOTE or balanced class weighting.
- **FR-04.2 Multi-Model Evaluation:** Train and evaluate Logistic Regression, Random Forest, and Gradient Boosting Classifiers.
- **FR-04.3 Comprehensive Metrics:** Report Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC, Confusion Matrix, and ROC Curve.
- **FR-04.4 Risk Tiering:** Categorize customers into Low Risk (<0.35), Medium Risk (0.35 - 0.65), and High Risk (>0.65) calibrated churn probabilities.
- **FR-04.5 Explainable AI:** Compute feature importance rankings and individualized top churn risk drivers for each assessed customer.

### FR-05: Retention Case Management Workflow
- **FR-05.1 Case Generation:** Automatically or manually enroll high-risk customers into retention queues.
- **FR-05.2 Lifecycle Statuses:** Track status transitions: `Identified` -> `Assigned` -> `Contacted` -> `Offer Proposed` -> `Retained` / `Not Retained` -> `Closed`.
- **FR-05.3 RM Assignment & Interaction Logging:** Record assigned Relationship Manager, target follow-up date, proposed retention incentive (fee waiver, rate boost, credit line), and free-text notes.
- **FR-05.4 Persistence:** All status updates and case logs must persist directly to the relational database with full audit timestamps.

### FR-06: Transaction Analytics & Reconciliation
- **FR-06.1 Volume & Channel Dynamics:** Aggregate daily, weekly, and monthly transactions across ATM, POS, Online, Mobile, and Branch channels.
- **FR-06.2 Spending & Cashflow Patterns:** Track deposit velocity vs withdrawal velocity, average ticket size, and seasonality.
- **FR-06.3 Analytical Reconciliation:** Audit record counts, ledger balance balance checks, duplicate transaction detection, and dormant account flags (>90 days inactive).

### FR-07: Campaign Intelligence & Attribution
- **FR-07.1 Campaign Management:** Maintain campaign objectives, budgets, start/end dates, and segment assignment.
- **FR-07.2 Performance Analytics:** Calculate Reach, Response Rate, Conversion Rate, Total Cost, Attributed Revenue, ROI, and Cost Per Acquisition (CPA).
- **FR-07.3 Attribution Transparency:** Support first-touch and last-touch attribution models with clear assumptions documented.

### FR-08: Branch Analytics & Regional Benchmarking
- **FR-08.1 Branch Performance Metrics:** Benchmark branch deposits, customer volume, loan origination, attrition rate, and revenue contribution.
- **FR-08.2 Regional Comparison:** Score and rank branches across performance tiers and highlight underperforming units requiring intervention.

### FR-09: Product Intelligence & Cross-Selling
- **FR-09.1 Penetration Metrics:** Track product penetration rates across Savings, Checking, Fixed Deposits, Personal Loans, Mortgages, and Credit Cards.
- **FR-09.2 Rule-Based Cross-Sell Identification:** Evaluate customer suitability rules (e.g., high balance with no term deposit -> Term Deposit recommendation; frequent travel spend with basic debit -> Premium Credit Card recommendation).

### FR-10: Business Reporting & Data Export Engine
- **FR-10.1 Standard Banking Reports:** Produce 8 executive reports with applied filters, KPIs, executive summary, and recommendations.
- **FR-10.2 Multi-Format Generator:** Export to CSV, XLSX (with styled sheets and header formatting), and PDF with banking branding.
