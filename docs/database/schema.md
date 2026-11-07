# BankSight Database Schema Documentation
## Complete Relational Database Specification
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Schema Overview
The BankSight database schema consists of 21 normalized relational tables designed to support transactional banking fidelity, high-speed analytical aggregations, and auditable operational workflows.

### Table Categorization
1. **Organizational Entities:** `branches`, `relationship_managers`.
2. **Customer Entities:** `customers`, `customer_interactions`, `complaints`.
3. **Core Account Entities:** `account_types`, `accounts`, `transactions`.
4. **Product & Lending Entities:** `products`, `customer_products`, `loans`.
5. **Marketing Campaign Entities:** `campaigns`, `campaign_assignments`, `campaign_responses`.
6. **Customer Intelligence & ML Entities:** `customer_segments`, `model_versions`, `churn_predictions`.
7. **Operational Retention Entities:** `retention_cases`, `retention_actions`.
8. **Pipeline & Governance Entities:** `data_import_jobs`, `data_quality_results`.

---

## 2. Table Definitions

### 1. `branches`
- `branch_id` VARCHAR(50) PRIMARY KEY: Unique branch identifier (e.g. `BRN-001`).
- `branch_name` VARCHAR(100) NOT NULL: Branch commercial name.
- `branch_code` VARCHAR(20) UNIQUE NOT NULL: Operational branch clearing code.
- `address` VARCHAR(200) NOT NULL: Street address.
- `city` VARCHAR(100) NOT NULL (Indexed): Branch city.
- `state` VARCHAR(50) NOT NULL (Indexed): Branch state.
- `postal_code` VARCHAR(20) NOT NULL: Postal zip code.
- `region` VARCHAR(50) NOT NULL (Indexed): Geographic region (Northeast, Midwest, South, West).
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE: Branch operating status.
- `created_at` DATETIME NOT NULL: Record creation timestamp.

### 2. `relationship_managers`
- `rm_id` VARCHAR(50) PRIMARY KEY: Manager identifier (e.g. `RM-001`).
- `branch_id` VARCHAR(50) NOT NULL REFERENCES `branches(branch_id)` (Indexed).
- `first_name` VARCHAR(50) NOT NULL: First name.
- `last_name` VARCHAR(50) NOT NULL: Last name.
- `email` VARCHAR(100) UNIQUE NOT NULL: Corporate email address.
- `phone` VARCHAR(30) NOT NULL: Direct telephone extension.
- `portfolio_size` INTEGER NOT NULL DEFAULT 0: Number of assigned high-value customers.
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE.
- `created_at` DATETIME NOT NULL.

### 3. `customers`
- `customer_id` VARCHAR(50) PRIMARY KEY: Customer identifier (e.g. `CUST-00001`).
- `first_name` VARCHAR(50) NOT NULL.
- `last_name` VARCHAR(50) NOT NULL.
- `email` VARCHAR(100) UNIQUE NOT NULL.
- `phone` VARCHAR(30) NOT NULL.
- `date_of_birth` DATE NOT NULL.
- `age` INTEGER NOT NULL (Indexed).
- `gender` VARCHAR(20) NOT NULL (Indexed).
- `occupation` VARCHAR(100) NOT NULL (Indexed).
- `annual_income` FLOAT NOT NULL: Annual gross income in USD.
- `address` VARCHAR(200) NOT NULL.
- `city` VARCHAR(100) NOT NULL (Indexed).
- `state` VARCHAR(50) NOT NULL (Indexed).
- `postal_code` VARCHAR(20) NOT NULL.
- `country` VARCHAR(50) NOT NULL DEFAULT 'USA'.
- `joining_date` DATE NOT NULL (Indexed).
- `customer_tenure_months` INTEGER NOT NULL.
- `customer_status` VARCHAR(30) NOT NULL DEFAULT 'Active' (Indexed).
- `customer_segment` VARCHAR(50) NOT NULL DEFAULT 'Standard' (Indexed).
- `branch_id` VARCHAR(50) NOT NULL REFERENCES `branches(branch_id)` (Indexed).
- `rm_id` VARCHAR(50) NULL REFERENCES `relationship_managers(rm_id)` (Indexed).
- `credit_score` INTEGER NULL.
- `kyc_verified` BOOLEAN NOT NULL DEFAULT TRUE.
- `digital_banking_active` BOOLEAN NOT NULL DEFAULT TRUE.
- `mobile_banking_active` BOOLEAN NOT NULL DEFAULT TRUE.
- `opt_in_marketing` BOOLEAN NOT NULL DEFAULT TRUE.
- `churn_flag` BOOLEAN NOT NULL DEFAULT FALSE (Indexed).
- `churn_date` DATE NULL.
- `created_at` DATETIME NOT NULL.
- `updated_at` DATETIME NOT NULL.

### 4. `accounts`
- `account_id` VARCHAR(50) PRIMARY KEY: Account ID (e.g. `ACC-00001`).
- `account_number` VARCHAR(50) UNIQUE NOT NULL (Indexed).
- `customer_id` VARCHAR(50) NOT NULL REFERENCES `customers(customer_id)` (Indexed).
- `type_id` VARCHAR(50) NOT NULL REFERENCES `account_types(type_id)` (Indexed).
- `branch_id` VARCHAR(50) NOT NULL REFERENCES `branches(branch_id)` (Indexed).
- `currency` VARCHAR(10) NOT NULL DEFAULT 'USD'.
- `current_balance` FLOAT NOT NULL DEFAULT 0.0.
- `available_balance` FLOAT NOT NULL DEFAULT 0.0.
- `average_balance_90d` FLOAT NOT NULL DEFAULT 0.0.
- `account_status` VARCHAR(30) NOT NULL DEFAULT 'Active' (Indexed).
- `open_date` DATE NOT NULL (Indexed).
- `close_date` DATE NULL.
- `is_primary` BOOLEAN NOT NULL DEFAULT FALSE.
- `created_at` DATETIME NOT NULL.
- `updated_at` DATETIME NOT NULL.

### 5. `transactions`
- `transaction_id` VARCHAR(50) PRIMARY KEY: Transaction ID (e.g. `TXN-000001`).
- `account_id` VARCHAR(50) NOT NULL REFERENCES `accounts(account_id)` (Indexed).
- `customer_id` VARCHAR(50) NOT NULL REFERENCES `customers(customer_id)` (Indexed).
- `branch_id` VARCHAR(50) NOT NULL REFERENCES `branches(branch_id)` (Indexed).
- `transaction_date` DATETIME NOT NULL (Indexed).
- `transaction_type` VARCHAR(30) NOT NULL (Deposit, Withdrawal, Transfer, Payment, Fee) (Indexed).
- `amount` FLOAT NOT NULL.
- `balance_after` FLOAT NOT NULL.
- `channel` VARCHAR(30) NOT NULL (ATM, POS, ONLINE, MOBILE, BRANCH) (Indexed).
- `status` VARCHAR(20) NOT NULL DEFAULT 'Completed' (Indexed).
- `description` VARCHAR(255) NULL.
- `merchant_category` VARCHAR(50) NULL.
- `created_at` DATETIME NOT NULL.
- Composite Indexes: `(customer_id, transaction_date)`, `(channel, transaction_type)`.

*(Refer to `docs/database/data_dictionary.md` for complete specification of all 21 tables).*

