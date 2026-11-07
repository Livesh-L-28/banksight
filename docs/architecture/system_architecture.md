# BankSight Enterprise Architecture Blueprint
## High-Level System Design & Component Architecture
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Architectural Vision & Principles
BankSight is architected as a modular, decoupled banking intelligence and operational retention platform following clean architecture principles. It strictly separates concerns between:
1. **Presentation Layer:** Enterprise Streamlit UI with 13 functional pages and interactive Plotly visualization.
2. **Analytics & Machine Learning Layer:** Feature engineering, scikit-learn predictive pipelines, RFM, and K-Means segmentation.
3. **Domain & Application Services:** Business logic orchestration, validation, reporting, and retention workflows.
4. **Data Access & Persistence Layer:** Normalized relational database (PostgreSQL / SQLite) via SQLAlchemy 2.0 ORM and repository patterns.
5. **Data Pipeline Layer:** Ingestion, data quality rules, cleaning, transformation, and audit logging.

---

## 2. High-Level System Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Presentation Layer"]
        UI["Streamlit Enterprise Banking App (Home.py + 13 Pages)"]
        PlotlyLib["Plotly Interactive Charts & Responsive Cards"]
        PDFGen["ReportLab PDF & OpenPyXL Excel Export Engine"]
    end

    subgraph ServiceLayer ["Application & Domain Services"]
        CustSvc["Customer 360 Service"]
        RetSvc["Retention Workflow Service"]
        SegSvc["Segmentation Service (RFM & K-Means)"]
        ChurnSvc["Churn ML Service (Inference & Calibration)"]
        TxnSvc["Transaction Analytics Service"]
        CampSvc["Campaign Attribution Service"]
        BrnSvc["Branch Benchmarking Service"]
        RepSvc["Business Reporting Service"]
    end

    subgraph PipelineLayer ["Data Engineering & Quality Pipeline"]
        Ingest["Ingestion Engine (CSV / XLSX)"]
        Val["Schema & Range Validation (Pydantic / Rules)"]
        Clean["Data Cleaning & Deduplication"]
        FeatEng["Temporal Feature Engineering Engine"]
        AuditLog["Data Quality Audit Logger"]
    end

    subgraph PersistenceLayer ["Persistence & Database Layer"]
        SQLA["SQLAlchemy 2.0 Engine & Session Pool"]
        Alembic["Alembic Database Migrations"]
        DB[("Relational Database: PostgreSQL 16+ / SQLite")]
    end

    subgraph PowerBILayer ["Power BI Semantic Layer"]
        StarSchema["Star Schema Views (Facts & Dims)"]
        DAX["Standardized DAX Measures"]
    end

    UI --> CustSvc
    UI --> RetSvc
    UI --> SegSvc
    UI --> ChurnSvc
    UI --> TxnSvc
    UI --> CampSvc
    UI --> BrnSvc
    UI --> RepSvc
    UI --> PlotlyLib
    UI --> PDFGen

    CustSvc --> SQLA
    RetSvc --> SQLA
    SegSvc --> SQLA
    ChurnSvc --> SQLA
    TxnSvc --> SQLA
    CampSvc --> SQLA
    BrnSvc --> SQLA
    RepSvc --> SQLA

    Ingest --> Val --> Clean --> FeatEng --> SQLA
    Val --> AuditLog --> SQLA

    SQLA --> DB
    Alembic --> DB
    DB --> StarSchema --> DAX
```

---

## 3. Technology Stack Reference Table

| Layer | Technologies Selected | Rationale |
|---|---|---|
| **Programming Language** | Python 3.12+ | High performance, modern typing, robust ecosystem for data science and web apps. |
| **User Interface** | Streamlit, Plotly, HTML/CSS Components | Rapid enterprise interactivity, real-time reactive re-rendering, deep financial color palettes. |
| **Data Processing** | Pandas, NumPy | Standard vectorized in-memory tabular manipulation and aggregations. |
| **Database & ORM** | PostgreSQL 16+, SQLAlchemy 2.0, Alembic | ACID-compliant relational persistence, declarative schemas, seamless SQLite fallback. |
| **Machine Learning** | Scikit-learn, Joblib, SHAP | Reliable production algorithms (Logistic Regression, Random Forest, Gradient Boosting), calibrated probabilities, and explainability. |
| **Reporting** | OpenPyXL, ReportLab | Native generation of styled Excel workbooks and audit-ready PDF documents. |
| **Semantic / BI** | Power BI Star Schema, DAX | Native corporate BI distribution and enterprise data democratization. |
| **Infrastructure & CI** | Docker, Docker Compose, GitHub Actions, Pytest, Ruff | Reproducible containerized execution, automated quality gates, zero regression. |

