# Detailed Functional Requirements Specification
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Traceable Functional Requirements

| Req ID | Module | Feature Description | Input Parameters | Processing Logic | Expected Output |
|---|---|---|---|---|---|
| **FR-EX-01** | Executive Dashboard | Summary KPI Calculation | Date range, branch IDs, segment IDs, product IDs | Query transactional and customer fact tables within active filters | Dynamic metric cards: Total Customers, Active Customers, Deposits, Churn Rate, Retention Rate, CLV, ARPU |
| **FR-EX-02** | Executive Dashboard | Visual Trend Analysis | Time grain (Monthly, Quarterly) | Aggregate net deposits, customer acquisition, and transaction volumes over time | Plotly interactive time-series line and bar charts with hover tooltips |
| **FR-EX-03** | Executive Dashboard | Filter Drill-Down | Segment/Branch click event | Filter underlying data structures to the selected cohort | Cohort data table displaying top 50 customers with pagination and export |
| **FR-C360-01**| Customer 360 | Customer Lookup | Customer ID, Name, Account # | Case-insensitive substring and exact key query against database index | Matching customer list with preview profile cards |
| **FR-C360-02**| Customer 360 | Full Profile Dossier | Selected Customer ID | Join `customers`, `accounts`, `products`, `transactions`, `interactions`, `complaints` | Comprehensive multi-tab dossier with balances, history, risk score, and RM notes |
| **FR-C360-03**| Customer 360 | Activity Timeline | Customer ID, Time Window | Fetch chronologically sorted log of transactions, interactions, complaints, campaign contacts | Interactive vertical timeline component with color-coded event icons |
| **FR-SEG-01** | Segmentation | RFM Calculation | Analysis date (defaults to current/max date) | 1. Recency = Min(days since last debit)<br>2. Frequency = Count(transactions in 12m)<br>3. Monetary = Sum(transaction amount) / Avg(balance) | RFM quintile scores (1-5) and segment labels (High Value, Loyal, At Risk, Dormant, etc.) |
| **FR-SEG-02** | Segmentation | K-Means Clustering | Feature set (Balance, Tenure, Frequency, Digital Ratio), cluster count $k \in [3, 8]$ | 1. MinMax/StandardScale features<br>2. Fit KMeans with `random_state=42`<br>3. Calculate cluster centroids and silhouette score | Profiled cluster dataframe with assigned business labels (e.g. "Wealth Elite", "Digital Youth") |
| **FR-ML-01**  | Churn Intelligence | Feature Engineering Pipeline | Cutoff date $T$ | Compute retrospective behavioral, balance, and complaint features strictly prior to $T$ | Standardized feature matrix $X$ and label vector $y$ with zero leakage |
| **FR-ML-02**  | Churn Intelligence | Multi-Model Benchmark | Training split (80%), Test split (20%) | Train Logistic Regression, Random Forest, Gradient Boosting; evaluate on test split | Comparison table with Accuracy, Precision, Recall, F1, ROC-AUC; interactive ROC/PR curves |
| **FR-ML-03**  | Churn Intelligence | Risk Scoring & Explanation | Customer feature vector | Apply selected champion model; generate calibrated probability $P(\text{churn})$; extract SHAP/tree weights | Calibrated probability, Risk Tier (Low/Medium/High), top 3 risk drivers, recommended action |
| **FR-RET-01** | Retention Management | Operational Case Creation | Customer ID, RM ID, Reason | Insert into `retention_cases` table with initial status `Identified` or `Assigned` | Newly created case record with unique Case ID and audit timestamp |
| **FR-RET-02** | Retention Management | Workflow Status Transition | Case ID, New Status, Notes, Offer | Update status (`Identified`, `Assigned`, `Contacted`, `Offer Proposed`, `Retained`, `Not Retained`, `Closed`), log entry in `retention_actions` | Persisted database record, updated case card, refreshed retention funnel metrics |
| **FR-TXN-01** | Transaction Analytics| Volume & Spend Aggregation | Channel, Type, Date Window | Group by Channel (ATM/POS/Mobile/Branch) and Type (Deposit/Withdrawal/Transfer) | Total volume, total value, average transaction size, channel share donut chart |
| **FR-TXN-02** | Transaction Analytics| Dormancy & Outlier Detection| Days threshold (e.g. 90 days), Z-score | Identify accounts with no debit activity for >90 days or transactions $> 3\sigma$ above mean | Flagged account lists for relationship manager review and reconciliation check |
| **FR-CMP-01** | Campaign Intelligence | Campaign ROI Attribution | Campaign ID, Attribution Model | Join campaign contacts with subsequent product originations and deposit increases | Reach, response %, conversion %, acquisition cost, attributed revenue, net ROI |
| **FR-BRN-01** | Branch Performance | Branch Benchmarking | Region, Branch ID | Aggregate deposits, customer acquisition, attrition, and loan volume per branch | Branch ranking table, regional performance radar chart, underperforming alerts |
| **FR-PRD-01** | Product Intelligence | Cross-Sell Rule Engine | Customer profile holdings | Evaluate cross-sell matrix rules against active customer product map | Personalized product opportunity recommendations with expected value |
| **FR-REP-01** | Reporting Engine | Multi-Format Export | Report Type, Filters, Format (CSV/XLSX/PDF) | Generate structured report with executive summary, metadata, KPI snapshot, and recommendations | Downloadable formatted file with proper headers, styling, and disclaimers |
