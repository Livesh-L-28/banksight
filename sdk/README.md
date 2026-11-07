# BankSight Python SDK

Official Python client library for the **BankSight Banking Customer Intelligence & Retention Platform**.

Designed for enterprise Core Banking systems (Temenos T24, Finacle, FIS), CRM platforms (Salesforce Financial Services Cloud), and data engineering automation.

---

## 🚀 Key Capabilities

- **OAuth2 Bearer Authentication:** Secure session management with automatic JWT injection.
- **Executive KPIs & Reconciliation:** Access real-time financial metrics and transaction ledger audits.
- **Customer 360 Dossier:** Full demographic, account, and transaction profiles with role-based dynamic PII masking.
- **ML Churn Scoring:** Calibrated probability scoring, risk tier assignment, and contributing factors.
- **SOX 404 Four-Eyes Dual-Authorization:** Programmatic submission and branch manager review of high-value retention concessions.
- **Generative AI Copilot:** Instant generation of executive meeting briefings, Do's & Don'ts talking points, and outreach letters.
- **Real-Time Streaming Ingestion:** Low-latency API for streaming ledger events and triggering capital flight alerts.
- **Model Risk Management (SR 11-7):** Programmatic retrieval of Fair Lending Disparate Impact and PSI drift reports.
- **Customer Lifetime Value (CLV) & Uplift Modeling:** 12m & 36m DCF Net Present Value valuations and causal retention quadrant classification.
- **Federal Reserve CCAR & Basel III Stress Testing:** Macroeconomic scenario shocks (Baseline, Adverse, Severely Adverse) and Liquidity Coverage Ratio (LCR) modeling.
- **HMAC-SHA256 Webhook Event Bus:** Real-time event notifications for Core Banking integration (FIS, Temenos, Fiserv).

---

## 📦 Installation

```bash
pip install -e .
```

---

## 💻 Quickstart

```python
from sdk.banksight_client import BankSightClient

# Initialize client
client = BankSightClient(base_url="http://localhost:8000")

# 1. Authenticate with enterprise credentials
client.login(username="admin", password="Admin@123")

# 2. Query Executive Banking KPIs
kpis = client.get_executive_kpis()
print(f"Total Active Customers: {kpis['active_customers']:,}")
print(f"Total Bank Deposits: ${kpis['total_deposits']:,.2f}")

# 3. Predict ML Churn Risk
prediction = client.predict_churn("CUST-000001")
print(f"Risk Tier: {prediction['risk_category']} (Score: {prediction['churn_probability']:.1%})")

# 4. Generate AI RM Briefing
briefing = client.generate_rm_briefing("CUST-000001")
print(f"Executive Summary: {briefing['briefing_executive_summary']}")

# 5. Stream Real-Time Withdrawal Event
response = client.stream_withdrawal_event({
    "transaction_id": "TX-STREAM-9921",
    "customer_id": "CUST-000001",
    "account_id": "ACC-0001",
    "amount": 45000.0,
    "prior_balance": 80000.0,
    "new_balance": 35000.0,
    "channel": "Wire Transfer",
    "timestamp": "2026-11-07T14:30:00Z"
})
print("Streaming Alert:", response["alert"])
```

---

## 🛡️ Error Handling

The SDK exposes granular exception classes:

```python
from sdk.banksight_client import (
    BankSightClient, AuthenticationError,
    PermissionDeniedError, ResourceNotFoundError, APIResponseError
)

client = BankSightClient()
try:
    client.login("invalid_user", "bad_pass")
except AuthenticationError as e:
    print("Invalid login credentials:", e)
except PermissionDeniedError as e:
    print("User role does not permit this action (RBAC):", e)
except ResourceNotFoundError as e:
    print("Requested customer or case not found:", e)
```
