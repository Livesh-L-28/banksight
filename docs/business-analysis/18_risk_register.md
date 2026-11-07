# Project Risk Register & Mitigation Strategy
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Risk Matrix

| Risk ID | Risk Category | Risk Description | Likelihood | Impact | Risk Level | Mitigation Strategy | Owner |
|---|---|---|---|---|---|---|---|
| **RSK-01** | Data Science / ML | **Model Data Leakage:** Use of future information (e.g. account closure date or post-churn transactions) in training churn models. | Low | Critical | **High** | Enforce strict cutoff date $T$; engineer all behavioral features strictly using records occurring before $T$. Validate via automated pipeline tests. | Lead ML Engineer |
| **RSK-02** | Regulatory / Compliance | **PII Exposure:** Accidental inclusion of real customer personal or financial records in repo or demo databases. | Low | Critical | **High** | Mandatory synthetic data generator with Faker; strict `.gitignore` on production databases; zero real PII in repository. | Compliance Officer |
| **RSK-03** | Operations | **Frontline Non-Adoption:** Relationship Managers ignore churn alerts due to mistrust of "black box" machine learning models. | Medium | High | **High** | Implement explainable AI displays (top contributing factors per customer) and advisory playbooks directly in the RM case view. | Head of Retention |
| **RSK-04** | Architecture / Perf | **Query Bottlenecks:** Large transaction tables cause dashboard timeouts during real-time aggregations. | Medium | Medium | **Medium** | Normalized relational schema with B-Tree indexes on `customer_id`, `branch_id`, `transaction_date`, and pre-aggregated KPI summaries. | Data Architect |
| **RSK-05** | Business Logic | **Correlational Campaign Bias:** Attributing organic product adoption to recent marketing campaigns without baseline controls. | Medium | Medium | **Medium** | Document attribution methodology clearly; support control group comparisons and transparent ROI assumptions. | Senior BI Analyst |
| **RSK-06** | System Integration | **Database Divergence:** Inconsistencies between PostgreSQL production schema and SQLite development environment. | Low | Medium | **Low** | Utilize SQLAlchemy 2.0 ORM agnostic dialect mapping and Alembic migrations tested in CI against both dialects. | DevOps / QA |
