# Project Scope & Boundary Specification
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Project Boundaries & System Context

BankSight is designed as an analytical decision-support and operational intelligence platform. It ingests, normalizes, analyzes, and models retail banking customer and transaction data to drive customer retention, executive decision-making, and marketing efficacy.

---

## 2. In-Scope Functional Capabilities

1. **Executive Banking Dashboard:**
   - Real-time aggregation of 15 essential banking KPIs.
   - Interactive date, branch, segment, and product slicing.
   - Drill-down navigation directly to customer records.

2. **Customer 360 Intelligence:**
   - Complete individual profile dossiers combining demographic, financial, and behavioral records.
   - Interactive transaction history, product holdings, and customer interaction logs.
   - Real-time customer search with multi-field matching.

3. **Multi-Dimensional Segmentation:**
   - Demographic, Geographic, and Financial rule-based segmentation.
   - Automated RFM (Recency, Frequency, Monetary) quintile scoring.
   - Unsupervised K-Means clustering with feature profiling and business labeling.

4. **Machine Learning Churn Prediction:**
   - Multi-model training and evaluation (Logistic Regression, Random Forest, Gradient Boosting).
   - Strict temporal split and zero data leakage.
   - Calibrated probability thresholds for Low, Medium, and High churn risk tiers.
   - Individual feature contribution analysis (SHAP and Tree Feature Importance).

5. **Operational Retention Case Management:**
   - Interactive retention case tracking with persistent database state.
   - Case workflow lifecycle: `Identified` -> `Assigned` -> `Contacted` -> `Offer Proposed` -> `Retained` / `Not Retained` -> `Closed`.
   - RM assignment, follow-up scheduling, and audit trail of interaction notes.

6. **Transaction Analytics & Channel Intelligence:**
   - Aggregated spending dynamics, velocity, and channel distribution (ATM, POS, Mobile, Online, Branch).
   - Dormant account detection (>90 days without debit).
   - Transaction reconciliation audits (count, volume, duplicate detection).

7. **Campaign & Marketing Intelligence:**
   - Campaign creation, budget tracking, customer assignment, and response logging.
   - Transparent multi-touch and single-touch revenue attribution modeling.
   - Marketing ROI, CPA, and conversion analysis by customer segment.

8. **Branch & Product Benchmarking:**
   - Branch ranking by deposits, customer growth, attrition, and loan originations.
   - Product penetration, cross-sell recommendation engine, and portfolio retention.

9. **Enterprise Reporting & Power BI Deliverables:**
   - On-demand export of 8 standard executive reports in CSV, Excel, and PDF formats.
   - Star schema tables, SQL views, and DAX measures ready for Power BI Desktop.

---

## 3. Explicitly Out-of-Scope Capabilities

1. **Core Banking Payment Processing:**
   - BankSight does not execute ACH, Fedwire, SWIFT, SEPA, or real-time credit/debit card ledger settlements. It is strictly an intelligence layer.
2. **Automated Credit Underwriting & Decisioning:**
   - The platform generates cross-sell opportunities (e.g. personal loan eligibility indicators) but does not bind credit agreements or replace FCRA-compliant credit scoring bureaus.
3. **Regulatory Anti-Money Laundering (AML) Reporting:**
   - While BankSight provides unusual transaction indicators for analytical hygiene, it does not file FinCEN Suspicious Activity Reports (SARs) or Currency Transaction Reports (CTRs).
4. **Third-Party Telephony / Call Center Dialer Integration:**
   - Direct automatic dialing, interactive voice response (IVR) hosting, or SMS gateway delivery are excluded; RMs utilize BankSight to view queues and record outcomes.
5. **Real Customer PII Data Processing:**
   - Production personally identifiable information (PII) is strictly prohibited. The platform operates on realistic, high-fidelity synthetic data preserving privacy.
