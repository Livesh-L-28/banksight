# BankSight Database Indexing Strategy
## Analytical & Transactional Query Optimization Guide
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Indexing Principles & Rationale
BankSight serves both operational point updates (such as updating a retention case status) and high-volume analytical aggregations (computing portfolio deposit totals across branches over time). To guarantee $<1.5$ second query execution, the indexing strategy combines:
1. **Single-Column B-Tree Indexes:** On all Foreign Keys (`customer_id`, `branch_id`, `rm_id`, `type_id`, `product_id`, `campaign_id`).
2. **Temporal Indexes:** On all event timestamps (`transaction_date`, `open_date`, `assigned_date`, `computed_date`).
3. **Status & Category Indexes:** On operational lifecycle columns (`customer_status`, `churn_flag`, `status`, `risk_level`, `segment_label`).
4. **Composite Indexes:** On high-frequency analytical join and aggregation paths.

---

## 2. High-Impact Composite Indexes

| Target Table | Composite Columns | Justification / Query Workload |
|---|---|---|
| `transactions` | `(customer_id, transaction_date)` | Speeds up RFM recency calculations, customer 360 transaction timelines, and trailing 90-day balance trends. |
| `transactions` | `(channel, transaction_type)` | Accelerates channel breakdown charts and deposit vs withdrawal velocity aggregations. |
| `customer_products` | `(customer_id, product_id)` | Enforces unique active enrollment and accelerates customer cross-sell rule evaluation. |
| `retention_cases` | `(status, risk_level)` | Optimizes the operational retention manager queue and SLA monitoring views. |
| `customers` | `(branch_id, customer_status)` | Powers branch benchmarking and regional active customer filters without full table scans. |

---

## 3. Maintenance & Vacuuming
- For PostgreSQL deployments, automated `VACUUM ANALYZE` runs nightly after batch ETL loading to keep planner statistics calibrated.
- For SQLite deployments, `PRAGMA optimize;` is executed periodically to maintain index tree balance.

