# User Stories Specification
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. User Story Matrix by Persona

### Persona: Retention Manager
- **US-RET-01:** As a Retention Manager, I want to filter and view customers with high churn probability so that I can prioritize urgent retention interventions before account closure.
- **US-RET-02:** As a Retention Manager, I want to inspect the primary drivers of churn risk for an individual customer so that I can formulate a targeted, high-affinity retention offer (e.g. fee waiver, rate bump, relationship manager meeting).
- **US-RET-03:** As a Retention Manager, I want to create a new retention case, assign it to a branch relationship manager, and set a target follow-up date so that accountability is clearly established.
- **US-RET-04:** As a Retention Manager, I want to view a real-time funnel of retention cases (Identified -> Assigned -> Contacted -> Offer Proposed -> Retained / Not Retained) so that I can report retention campaign efficiency to executive leadership.

### Persona: Relationship Manager (RM)
- **US-RM-01:** As a Relationship Manager, I want to search for a customer by name, account number, or customer ID to pull up their complete 360-degree profile before a consultation call.
- **US-RM-02:** As a Relationship Manager, I want to view a customer's chronological interaction timeline (transactions, complaints, digital logins) so that I understand recent friction points or service issues.
- **US-RM-03:** As a Relationship Manager, I want to update the status of my assigned retention cases and log detailed consultation notes so that the customer record reflects our latest touchpoint.
- **US-RM-04:** As a Relationship Manager, I want to view automated cross-sell and up-sell recommendations based on transparent business rules so that I can advise the client on products that truly fit their financial profile.

### Persona: Banking Executive / Head of Retail Banking
- **US-EXEC-01:** As an Executive, I want to view high-level banking KPIs (Total Deposits, Active Customers, Churn Rate, Retention Rate, ARPU, CLV) on a unified executive dashboard so that I can evaluate macroeconomic portfolio health at a glance.
- **US-EXEC-02:** As an Executive, I want to slice dashboard metrics by date range, branch network, and customer segment so that I can identify localized risks or outperforming regions.
- **US-EXEC-03:** As an Executive, I want to export board-ready performance reports in PDF and Excel formats with a single click so that I can share findings during quarterly executive steerco meetings.

### Persona: Branch Manager
- **US-BM-01:** As a Branch Manager, I want to compare my branch's deposit growth, customer acquisition, and attrition against regional peer branches so that I can pinpoint operational weaknesses.
- **US-BM-02:** As a Branch Manager, I want to identify dormant accounts (>90 days without activity) assigned to my branch so that my staff can initiate re-engagement outreach.

### Persona: Marketing Campaign Manager
- **US-MKT-01:** As a Campaign Manager, I want to define target customer cohorts based on RFM segments or K-Means clusters so that our product marketing messages resonate with specific customer personas.
- **US-MKT-02:** As a Campaign Manager, I want to evaluate campaign performance metrics (Reach, Response Rate, Conversion Rate, CAC, ROI) under documented attribution assumptions so that I can allocate marketing budgets effectively.

### Persona: Banking Data Analyst
- **US-DA-01:** As a Data Analyst, I want to train, compare, and validate multiple machine learning models (Logistic Regression, Random Forest, Gradient Boosting) using standard evaluation metrics (AUC, F1, Precision, Recall) so that I can ensure model rigor and absence of data leakage.
- **US-DA-02:** As a Data Analyst, I want star-schema analytical tables and verified DAX measures exported for Power BI so that our business intelligence team can build custom reporting views effortlessly.

