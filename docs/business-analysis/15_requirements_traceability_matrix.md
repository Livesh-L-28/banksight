# Requirements Traceability Matrix (RTM)
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Traceability Mapping Table

| BRD Req ID | Functional Req (FRD) | System Component | Database Entity | Test Case ID | Status |
|---|---|---|---|---|---|
| **BR-01 (Executive KPIs)** | FR-EX-01, FR-EX-02 | `app/pages/01_Overview.py`, `backend/repositories/kpi_repo.py` | `customers`, `accounts`, `transactions` | `TC-KPI-001`, `TC-E2E-001` | Mapped |
| **BR-02 (Customer 360)** | FR-C360-01, FR-C360-02 | `app/pages/02_Customer_360.py`, `backend/services/customer_service.py` | `customers`, `accounts`, `products`, `interactions` | `TC-C360-001`, `TC-C360-002` | Mapped |
| **BR-03 (Customer Segmentation)** | FR-SEG-01, FR-SEG-02 | `app/pages/03_Segmentation.py`, `analytics/segmentation/rfm.py`, `kmeans.py` | `customer_segments`, `transactions` | `TC-SEG-001`, `TC-SEG-002` | Mapped |
| **BR-04 (Churn ML Pipeline)** | FR-ML-01, FR-ML-02, FR-ML-03 | `app/pages/04_Churn_Intelligence.py`, `analytics/churn/pipeline.py` | `churn_predictions`, `model_versions` | `TC-ML-001`, `TC-ML-002`, `TC-ML-003` | Mapped |
| **BR-05 (Retention Workflow)** | FR-RET-01, FR-RET-02 | `app/pages/05_Retention_Management.py`, `backend/repositories/retention_repo.py` | `retention_cases`, `retention_actions` | `TC-RET-001`, `TC-RET-002` | Mapped |
| **BR-06 (Transaction Analytics)** | FR-TXN-01, FR-TXN-02 | `app/pages/06_Transaction_Analytics.py`, `analytics/transaction_analytics/` | `transactions`, `accounts` | `TC-TXN-001`, `TC-TXN-002` | Mapped |
| **BR-07 (Campaign Analytics)** | FR-CMP-01 | `app/pages/07_Campaign_Intelligence.py`, `analytics/campaign/` | `campaigns`, `campaign_assignments`, `campaign_responses` | `TC-CMP-001` | Mapped |
| **BR-08 (Branch Analytics)** | FR-BRN-01 | `app/pages/08_Branch_Analytics.py`, `analytics/branch/` | `branches`, `customers`, `accounts` | `TC-BRN-001` | Mapped |
| **BR-09 (Product Intelligence)** | FR-PRD-01 | `app/pages/09_Product_Intelligence.py`, `analytics/product/` | `products`, `customer_products`, `loans` | `TC-PRD-001` | Mapped |
| **BR-10 (Reporting Engine)** | FR-REP-01 | `app/pages/10_Reports.py`, `backend/services/reporting_service.py` | All Fact & Dim Tables | `TC-REP-001` | Mapped |
| **BR-11 (Data Management)** | FR-DATA-01 | `app/pages/11_Data_Management.py`, `data_pipeline/` | `data_import_jobs`, `data_quality_results` | `TC-DATA-001` | Mapped |
| **BR-12 (Power BI Deliverables)** | FR-PBI-01 | `powerbi/datasets/`, `powerbi/dax/`, `powerbi/sql_views/` | Power BI Star Schema Views | `TC-PBI-001` | Mapped |

