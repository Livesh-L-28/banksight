# BankSight Platform Changelog

All notable changes to the BankSight platform are documented in this file in adherence to Semantic Versioning.

---

## [1.0.0] — 2026-11-07

### Added
- **Module 1 (Executive Dashboard):** 15 dynamic banking KPIs, monthly deposit/withdrawal flow trends, segment donut distribution, branch rankings, and CSV cohort drill-down export.
- **Module 2 (Customer 360):** Unified customer intelligence dossiers, multi-account balances, loan facilities, complaints log, and chronological interaction timeline.
- **Module 3 (Customer Segmentation):** Demographic, Geographic, and Financial segmentation; RFM quintile scoring (1-5); unsupervised K-Means clustering with empirical centroid profiling and business playbooks.
- **Module 4 (Churn Intelligence):** Predictive machine learning pipeline benchmarking Logistic Regression, Random Forest, and Gradient Boosting; calibrated probabilities; top feature risk factor attributions; and advisory retention actions.
- **Module 5 (Retention Management):** Closed-loop operational case management with persistent database transitions (`Identified` -> `Assigned` -> `Contacted` -> `Offer Proposed` -> `Retained`), RM assignment, and retention funnel analytics.
- **Module 6 (Transaction Analytics):** Payment channel volume breakdown (Mobile, Online, POS, ATM, Branch), spending categories, dormant account alerts (>90 days), and ledger reconciliation checks.
- **Module 7 (Campaign Intelligence):** Campaign tracking, multi-touch revenue attribution modeling, marketing ROI, CPA, and conversion analytics.
- **Module 8 (Branch Analytics):** Branch deposit rankings, attrition rates, regional benchmarking, and underperforming unit alerts.
- **Module 9 (Product Intelligence):** Product penetration metrics, portfolio depth, and transparent rule-based cross-sell recommendations.
- **Module 10 (Business Reporting):** Multi-format export engine supporting 8 standard boardroom reports in CSV, styled Excel (.xlsx), and PDF formats.
- **Module 11 (Data Management):** File ingestion, schema validation, boundary checks, duplicate detection, and data quality execution logs.
- **Module 12 (Model Management):** MLOps model registry, version tracking, champion-challenger lineage, and feature importance governance.
- **Module 13 (Platform Settings):** Environment configuration, database connectivity audits, and risk threshold calibration.
- **Database & Architecture:** Normalized 21-entity relational schema with SQLAlchemy 2.0 ORM, Alembic migrations, and PostgreSQL/SQLite duality.
- **Power BI Semantic Layer:** Star Schema views (FactTransactions, FactCustomerSnapshot, FactCampaign, FactRetention, DimCustomer, DimDate, DimBranch, DimProduct, DimAccount), DAX measures library, and multi-tab Excel model workbook.
- **Testing & Quality:** Pytest test suite with 31 automated unit, integration, and e2e smoke tests passing; Ruff linting at 100% compliance.
- **DevOps & Infrastructure:** Multi-container `docker-compose.yml` with PostgreSQL 16 Alpine and Streamlit application, `Dockerfile`, `Makefile`, and GitHub Actions CI workflow.

