# BankSight Security Policy & Standards

## 1. Security Overview
BankSight is engineered for enterprise banking analytics and retention intelligence. Protecting data integrity, ensuring secure configuration, and enforcing privacy-preserving development practices are foundational design principles.

---

## 2. Core Security & Compliance Controls

### 2.1 Synthetic Data Privacy Standard
- **Zero Production PII:** Under no circumstances shall real customer names, Social Security Numbers (SSNs), real account numbers, real addresses, or unmasked credit cards exist within this repository.
- **Faker & Statistical Synthesis:** All data is synthetically produced with realistic behavioral patterns and Benford's Law distribution alignment without real individual identity linkage.

### 2.2 SQL Injection Prevention
- **Strict Parameterization:** 100% of database interactions are orchestrated via SQLAlchemy 2.0 ORM expressions or explicitly parameterized ANSI-SQL queries (`:param` / `?`).
- **No Raw String Formatting:** Unsanitized string concatenations (`f"SELECT ... WHERE id = '{input}'"`) are strictly prohibited in repositories.

### 2.3 Secrets & Environment Isolation
- **Dotenv Isolation:** All database credentials, secrets, host configurations, and environment keys are managed strictly via `.env` environment variables.
- **Gitignore Enforcement:** `.env`, `.pem`, `.key`, and local database binaries are excluded from version control in `.gitignore`.

### 2.4 File Ingestion Hardening
- **Extension Allowlist:** File loaders restrict file uploads to `.csv`, `.xlsx`, and `.xls`.
- **Size Boundaries:** Ingestion endpoints enforce a default 25MB ceiling to prevent buffer overflow or denial-of-service memory exhaustion.
- **Quarantine Protocol:** Malformed or suspicious records are redirected to `data/exports/rejected_records.csv` rather than silently executed.

### 2.5 Explainable & Advisory AI Governance
- **Human-in-the-Loop:** Machine learning churn probabilities and cross-sell suggestions are advisory. The system enforces human confirmation by an authorized Relationship Manager before binding retention incentives or customer communications are dispatched.
- **Zero Future Data Leakage:** Cutoff dates prevent models from using retrospective future information during evaluation.

---

## 3. Reporting Vulnerabilities
If you discover a potential security vulnerability within BankSight, please report it privately by contacting:
- **Security Contact:** `liveshjaidj@gmail.com`
- Do not disclose suspected security vulnerabilities publicly in GitHub issues.

