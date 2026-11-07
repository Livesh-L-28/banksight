# Non-Functional Requirements Specification (NFR)
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Performance Requirements
- **NFR-PERF-01 Query Latency:** Core analytical dashboard views must render within 1.5 seconds for datasets up to 100,000 transactions and 10,000 customers.
- **NFR-PERF-02 Search Response:** Customer search lookup by ID or name substring must return matching results in less than 300 milliseconds.
- **NFR-PERF-03 Model Inference:** Batch churn scoring for 5,000 customers must execute in less than 5.0 seconds on standard dual-core CPU architecture.
- **NFR-PERF-04 Export Generation:** Excel and PDF report exports must compile and start downloading within 3.0 seconds.

## 2. Scalability & Data Volume Requirements
- **NFR-SCAL-01 Horizontal & Vertical Growth:** The database schema and analytical queries must support up to 1,000,000 transaction records and 50,000 customers without structural changes.
- **NFR-SCAL-02 Memory Footprint:** The Streamlit application must operate within a 1.0 GB RAM memory ceiling, using efficient Pandas data types (categoricals, int32, float32) and SQL aggregations.

## 3. Reliability & Availability
- **NFR-REL-01 Zero Data Loss:** All retention case updates, interaction notes, and campaign modifications must be wrapped in ACID-compliant database transactions.
- **NFR-REL-02 Graceful Degradation:** If optional components (such as local SHAP visualization or external visualization libraries) encounter an environment limitation, the system must fall back transparently to tree-based feature importance without crashing.
- **NFR-REL-03 Dual Database Compatibility:** System must function out-of-the-box on SQLite for lightweight zero-dependency local testing and demonstrations, while seamlessly supporting enterprise PostgreSQL 16+ via SQLAlchemy connection strings for production and CI.

## 4. Security & Privacy
- **NFR-SEC-01 Parameterized SQL Queries:** All database interactions must use SQLAlchemy ORM or strictly parameterized queries to eliminate SQL injection vectors.
- **NFR-SEC-02 Synthetic Data Mandate:** All demo and training datasets must be 100% synthetic; no real personally identifiable information (PII), social security numbers, or real bank account numbers shall ever exist in the codebase or repository.
- **NFR-SEC-03 Secrets Management:** No database passwords, secret keys, or authentication tokens shall be hardcoded in repository files; all configurations must be loaded via `.env` environment variables.
- **NFR-SEC-04 File Upload Restrictions:** Data import endpoints must enforce strict file extension checks (`.csv`, `.xlsx`, `.xls`) and maximum file size limits (default 25MB) to prevent denial-of-service.

## 5. Usability & Accessibility
- **NFR-USA-01 Banking Design Standards:** The user interface must employ a clean, restrained, high-contrast navy/blue visual palette consistent with enterprise financial institutions.
- **NFR-USA-02 Responsive Layout:** Application layout must adapt fluidly across standard desktop and laptop resolutions (1280x720 up to 3840x2160).
- **NFR-USA-03 Meaningful Empty & Error States:** All views must render informative empty state guidance rather than raw Python stack traces when filters return zero records.

## 6. Maintainability & Code Quality
- **NFR-MNT-01 Automated Test Coverage:** Automated unit and integration test coverage must exceed 80% across backend models, data transformation pipelines, KPI calculation logic, and ML evaluation routines.
- **NFR-MNT-02 Code Quality Standards:** Codebase must conform to modern Python PEP 8 standards enforced by Ruff with 0 critical linting or formatting errors.
