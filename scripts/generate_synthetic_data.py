"""
BankSight High-Fidelity Synthetic Banking Data Generator
Generates realistic, referentially-consistent retail banking datasets adhering to
realistic financial distributions, Benford's law patterns, balance continuity,
and behavioral churn precursors without real PII.
"""

import os
import sys
import random
from datetime import datetime, date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from faker import Faker

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
fake = Faker()
Faker.seed(RANDOM_SEED)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_branches(n_branches=10):
    """Generates banking branch network records."""
    branches_data = [
        ("BRN-001", "Downtown Central Branch", "DCB-101", "100 Financial Way", "New York", "NY", "10005", "Northeast"),
        ("BRN-002", "Midtown Commercial Branch", "MCB-102", "450 Lexington Ave", "New York", "NY", "10017", "Northeast"),
        ("BRN-003", "Boston Harbor Branch", "BHB-103", "200 State Street", "Boston", "MA", "02109", "Northeast"),
        ("BRN-004", "Chicago Loop Branch", "CLB-104", "120 S LaSalle St", "Chicago", "IL", "60603", "Midwest"),
        ("BRN-005", "Detroit Metro Branch", "DMB-105", "500 Woodward Ave", "Detroit", "MI", "48226", "Midwest"),
        ("BRN-006", "Charlotte Financial Center", "CFC-106", "300 S Tryon St", "Charlotte", "NC", "28202", "Southeast"),
        ("BRN-007", "Atlanta Midtown Branch", "AMB-107", "1075 Peachtree St NE", "Atlanta", "GA", "30309", "Southeast"),
        ("BRN-008", "Dallas Uptown Branch", "DUB-108", "2100 McKinney Ave", "Dallas", "TX", "75201", "South"),
        ("BRN-009", "Denver Capitol Branch", "DCB-109", "1700 Lincoln St", "Denver", "CO", "80203", "West"),
        ("BRN-010", "San Francisco Financial Branch", "SFF-110", "555 California St", "San Francisco", "CA", "94104", "West"),
    ]
    records = []
    for b_id, name, code, addr, city, state, zip_c, region in branches_data[:n_branches]:
        records.append({
            "branch_id": b_id,
            "branch_name": name,
            "branch_code": code,
            "address": addr,
            "city": city,
            "state": state,
            "postal_code": zip_c,
            "region": region,
            "is_active": True,
            "created_at": datetime(2020, 1, 1, 9, 0, 0).isoformat()
        })
    return pd.DataFrame(records)


def generate_relationship_managers(branches_df, n_rms=25):
    """Generates branch relationship managers."""
    records = []
    branch_ids = branches_df["branch_id"].tolist()
    for i in range(1, n_rms + 1):
        b_id = branch_ids[(i - 1) % len(branch_ids)]
        fname = fake.first_name()
        lname = fake.last_name()
        records.append({
            "rm_id": f"RM-{i:03d}",
            "branch_id": b_id,
            "first_name": fname,
            "last_name": lname,
            "email": f"{fname.lower()}.{lname.lower()}@banksight-corp.com",
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "portfolio_size": random.randint(20, 60),
            "is_active": True,
            "created_at": datetime(2021, 1, 15, 8, 30, 0).isoformat()
        })
    return pd.DataFrame(records)


def generate_account_types():
    """Generates standard retail banking account types."""
    records = [
        {"type_id": "TYP-CHK-STD", "type_name": "Standard Checking", "category": "Deposit", "interest_rate_pct": 0.05, "monthly_fee": 12.00, "minimum_balance_req": 500.00, "description": "Day-to-day transaction checking with debit card"},
        {"type_id": "TYP-CHK-PRM", "type_name": "Premium Interest Checking", "category": "Deposit", "interest_rate_pct": 1.25, "monthly_fee": 25.00, "minimum_balance_req": 5000.00, "description": "High-tier interest earning checking with fee waivers"},
        {"type_id": "TYP-SAV-HY", "type_name": "High-Yield Savings", "category": "Deposit", "interest_rate_pct": 4.15, "monthly_fee": 0.00, "minimum_balance_req": 1000.00, "description": "Competitive high-yield digital liquid savings"},
        {"type_id": "TYP-SAV-STD", "type_name": "Standard Regular Savings", "category": "Deposit", "interest_rate_pct": 0.50, "monthly_fee": 5.00, "minimum_balance_req": 200.00, "description": "Basic emergency fund savings account"},
        {"type_id": "TYP-CD-12M", "type_name": "12-Month Certificate of Deposit", "category": "Investment", "interest_rate_pct": 5.00, "monthly_fee": 0.00, "minimum_balance_req": 2500.00, "description": "Fixed 12-month guaranteed return deposit certificate"},
        {"type_id": "TYP-MMA", "type_name": "Money Market Premier", "category": "Deposit", "interest_rate_pct": 3.75, "monthly_fee": 15.00, "minimum_balance_req": 10000.00, "description": "Tiered money market with check-writing capabilities"},
    ]
    return pd.DataFrame(records)


def generate_products():
    """Generates standard retail banking product catalog."""
    records = [
        {"product_id": "PRD-CHK-01", "product_code": "CHK_STD", "product_name": "Everyday Checking", "category": "Deposit", "annual_fee": 0.0, "interest_rate_pct": 0.05, "target_segment": "All", "is_active": True},
        {"product_id": "PRD-SAV-01", "product_code": "SAV_HYLD", "product_name": "High-Yield Savings", "category": "Deposit", "annual_fee": 0.0, "interest_rate_pct": 4.15, "target_segment": "Savers", "is_active": True},
        {"product_id": "PRD-CD-01", "product_code": "CD_1YR", "product_name": "1-Year Fixed Deposit", "category": "Deposit", "annual_fee": 0.0, "interest_rate_pct": 5.00, "target_segment": "Wealth & Affluent", "is_active": True},
        {"product_id": "PRD-CRD-01", "product_code": "CRD_PLAT", "product_name": "Platinum Rewards Credit Card", "category": "Card", "annual_fee": 95.0, "interest_rate_pct": 19.99, "target_segment": "Affluent Spenders", "is_active": True},
        {"product_id": "PRD-CRD-02", "product_code": "CRD_CASH", "product_name": "Cashback Unlimited Card", "category": "Card", "annual_fee": 0.0, "interest_rate_pct": 22.49, "target_segment": "Young Professionals", "is_active": True},
        {"product_id": "PRD-LOAN-01", "product_code": "LN_AUTO", "product_name": "Auto Loan 60M", "category": "Loan", "annual_fee": 0.0, "interest_rate_pct": 6.49, "target_segment": "Borrowers", "is_active": True},
        {"product_id": "PRD-LOAN-02", "product_code": "LN_PERS", "product_name": "Personal Signature Loan", "category": "Loan", "annual_fee": 50.0, "interest_rate_pct": 9.99, "target_segment": "Borrowers", "is_active": True},
        {"product_id": "PRD-MTG-01", "product_code": "MTG_30Y", "product_name": "30-Year Fixed Mortgage", "category": "Loan", "annual_fee": 0.0, "interest_rate_pct": 6.85, "target_segment": "Homeowners", "is_active": True},
    ]
    return pd.DataFrame(records)


def generate_customers(branches_df, rms_df, n_customers=1000):
    """Generates realistic customer demographics with embedded churn precursor traits."""
    records = []
    occupations = [
        "Software Engineer", "Registered Nurse", "Accountant", "Physician", "Marketing Manager",
        "Teacher", "Financial Analyst", "Operations Manager", "Sales Executive", "Attorney",
        "Civil Engineer", "Data Scientist", "Pharmacist", "Graphic Designer", "Retired Executive"
    ]
    branch_map = branches_df.set_index("branch_id").to_dict(orient="index")
    rm_ids = rms_df["rm_id"].tolist()
    branch_ids = branches_df["branch_id"].tolist()

    base_date = date(2026, 11, 1)

    for i in range(1, n_customers + 1):
        c_id = f"CUST-{i:05d}"
        b_id = random.choice(branch_ids)
        b_info = branch_map[b_id]

        # Age distribution: 21 to 78, weighted towards 30-55
        age = int(np.clip(np.random.normal(42, 13), 21, 80))
        birth_year = 2026 - age
        dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))

        # Income: log-normal distribution around $85k
        income = float(np.round(np.random.lognormal(mean=11.2, sigma=0.65), -2))
        income = max(26000.0, min(income, 450000.0))

        # Tenure: 4 to 120 months
        tenure_months = int(np.clip(np.random.exponential(scale=38) + 6, 4, 120))
        joining_date = base_date - timedelta(days=int(tenure_months * 30.4))

        gender = random.choice(["Male", "Female"])
        fname = fake.first_name_male() if gender == "Male" else fake.first_name_female()
        lname = fake.last_name()
        email = f"{fname.lower()}.{lname.lower()}{random.randint(10, 999)}@{fake.free_email_domain()}"

        # Assign RM for high income or randomly
        rm_id = random.choice(rm_ids) if (income > 90000 or random.random() < 0.4) else None

        # Churn simulation logic (~16% realistic portfolio churn)
        # Precursors: lower tenure, dissatisfaction, or sudden balance drops
        churn_prob_latent = 0.08
        if tenure_months < 18:
            churn_prob_latent += 0.08
        if income < 45000:
            churn_prob_latent += 0.06
        if age < 30:
            churn_prob_latent += 0.05

        is_churned = (random.random() < churn_prob_latent)
        churn_date = None
        status = "Active"
        if is_churned:
            days_ago = random.randint(10, 120)
            churn_date = base_date - timedelta(days=days_ago)
            status = "Inactive"

        # Customer segment
        if income > 180000:
            segment = "High Net Worth"
        elif income > 100000:
            segment = "Affluent"
        elif age < 30:
            segment = "Young Professional"
        elif tenure_months > 60:
            segment = "Loyal Traditional"
        else:
            segment = "Mass Retail"

        credit_score = int(np.clip(np.random.normal(715, 65), 520, 850))

        records.append({
            "customer_id": c_id,
            "first_name": fname,
            "last_name": lname,
            "email": email,
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "date_of_birth": dob.isoformat(),
            "age": age,
            "gender": gender,
            "occupation": random.choice(occupations),
            "annual_income": income,
            "address": fake.street_address(),
            "city": b_info["city"],
            "state": b_info["state"],
            "postal_code": b_info["postal_code"],
            "country": "USA",
            "joining_date": joining_date.isoformat(),
            "customer_tenure_months": tenure_months,
            "customer_status": status,
            "customer_segment": segment,
            "branch_id": b_id,
            "rm_id": rm_id,
            "credit_score": credit_score,
            "kyc_verified": True,
            "digital_banking_active": random.random() < 0.88 if not is_churned else random.random() < 0.45,
            "mobile_banking_active": random.random() < 0.82 if not is_churned else random.random() < 0.35,
            "opt_in_marketing": random.random() < 0.75,
            "churn_flag": is_churned,
            "churn_date": churn_date.isoformat() if churn_date else None,
            "created_at": datetime.combine(joining_date, datetime.min.time()).isoformat(),
            "updated_at": datetime(2026, 11, 1, 10, 0, 0).isoformat()
        })
    return pd.DataFrame(records)


def generate_accounts_and_transactions(customers_df, account_types_df, branches_df):
    """
    Generates accounts and realistic transaction histories with balance continuity:
    balance_after = balance_before + deposit / - withdrawal
    """
    accounts_records = []
    transactions_records = []
    customer_products_records = []

    account_types = account_types_df["type_id"].tolist()
    end_date = datetime(2026, 11, 1, 18, 0, 0)
    txn_id_counter = 1
    acc_id_counter = 1
    cp_id_counter = 1

    channels = ["MOBILE", "ONLINE", "POS", "ATM", "BRANCH"]
    channel_weights = [0.42, 0.28, 0.18, 0.08, 0.04]

    categories_spend = ["Groceries", "Dining", "Utilities", "Retail", "Travel", "Healthcare", "Entertainment"]

    for _, cust in customers_df.iterrows():
        c_id = cust["customer_id"]
        b_id = cust["branch_id"]
        joining_dt = datetime.fromisoformat(cust["joining_date"])
        is_churned = cust["churn_flag"]
        annual_inc = cust["annual_income"]

        # Number of accounts per customer (1 to 3)
        n_accounts = 1
        if cust["customer_segment"] in ["High Net Worth", "Affluent"]:
            n_accounts = random.choice([2, 3])
        elif random.random() < 0.45:
            n_accounts = 2

        # Primary checking account
        for acc_idx in range(n_accounts):
            acc_id = f"ACC-{acc_id_counter:06d}"
            acc_num = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{acc_id_counter:04d}"
            acc_id_counter += 1

            if acc_idx == 0:
                type_id = "TYP-CHK-PRM" if annual_inc > 100000 else "TYP-CHK-STD"
                is_prim = True
                open_dt = joining_dt
            else:
                type_id = random.choice(["TYP-SAV-HY", "TYP-SAV-STD", "TYP-CD-12M", "TYP-MMA"])
                is_prim = False
                open_dt = joining_dt + timedelta(days=random.randint(30, 300))
                if open_dt > end_date:
                    open_dt = joining_dt

            # Customer product record
            prod_id_match = "PRD-CHK-01" if "CHK" in type_id else ("PRD-SAV-01" if "SAV" in type_id else "PRD-CD-01")
            customer_products_records.append({
                "cust_prod_id": f"CP-{cp_id_counter:06d}",
                "customer_id": c_id,
                "product_id": prod_id_match,
                "enrollment_date": open_dt.date().isoformat(),
                "status": "Inactive" if is_churned else "Active",
                "created_at": open_dt.isoformat()
            })
            cp_id_counter += 1

            # Simulate transactions for this account
            # Active duration: from open_dt to churn_date (if churned) or end_date
            account_end_dt = end_date
            if is_churned and cust["churn_date"]:
                account_end_dt = datetime.fromisoformat(cust["churn_date"])

            days_active = max(10, (account_end_dt - open_dt).days)
            # Sample transactions within past 180-365 days
            txn_start_dt = max(open_dt, end_date - timedelta(days=365))

            # Initial opening balance
            initial_deposit = round(random.uniform(500.0, 5000.0) if annual_inc < 80000 else random.uniform(5000.0, 45000.0), 2)
            current_balance = initial_deposit

            # Add opening transaction
            transactions_records.append({
                "transaction_id": f"TXN-{txn_id_counter:07d}",
                "account_id": acc_id,
                "customer_id": c_id,
                "branch_id": b_id,
                "transaction_date": open_dt.isoformat(),
                "transaction_type": "Deposit",
                "amount": initial_deposit,
                "balance_after": current_balance,
                "channel": "BRANCH",
                "status": "Completed",
                "description": "Initial Account Funding Deposit",
                "merchant_category": "Funding",
                "created_at": open_dt.isoformat()
            })
            txn_id_counter += 1

            # Determine transaction frequency
            # Churned customers have low or decaying frequency
            avg_txns_per_month = random.randint(4, 18) if not is_churned else random.randint(1, 5)
            total_txns = int((days_active / 30.4) * avg_txns_per_month)
            total_txns = max(2, min(total_txns, 45))  # Keep realistic and performant

            # Generate chronological transactions
            step_days = max(1, days_active // total_txns)
            cur_txn_time = txn_start_dt

            for _t_i in range(total_txns):
                cur_txn_time += timedelta(days=random.randint(1, max(2, step_days)), hours=random.randint(1, 12))
                if cur_txn_time >= account_end_dt:
                    break

                # 40% deposits, 60% withdrawals
                is_deposit = random.random() < 0.38
                ch = np.random.choice(channels, p=channel_weights)

                if is_deposit:
                    # Salary or transfer deposit
                    amount = round(random.uniform(200.0, annual_inc / 24.0), 2)
                    current_balance += amount
                    ttype = "Deposit"
                    desc = "Payroll Direct Deposit" if random.random() < 0.6 else "ACH Inbound Transfer"
                    mcat = "Income"
                else:
                    # Spending withdrawal
                    max_possible = max(10.0, current_balance * 0.4)
                    amount = round(random.uniform(8.50, min(max_possible, 1200.0)), 2)
                    if current_balance - amount < 0:
                        amount = round(max(5.0, current_balance * 0.9), 2)
                    current_balance = max(0.0, current_balance - amount)
                    ttype = "Withdrawal"
                    desc = f"Purchase - {fake.company()}"
                    mcat = random.choice(categories_spend)

                transactions_records.append({
                    "transaction_id": f"TXN-{txn_id_counter:07d}",
                    "account_id": acc_id,
                    "customer_id": c_id,
                    "branch_id": b_id,
                    "transaction_date": cur_txn_time.isoformat(),
                    "transaction_type": ttype,
                    "amount": amount,
                    "balance_after": round(current_balance, 2),
                    "channel": ch,
                    "status": "Completed",
                    "description": desc,
                    "merchant_category": mcat,
                    "created_at": cur_txn_time.isoformat()
                })
                txn_id_counter += 1

            # If churned, balance drops to near-zero
            if is_churned and current_balance > 50.0:
                drain_amount = round(current_balance - random.uniform(0.0, 15.0), 2)
                current_balance -= drain_amount
                transactions_records.append({
                    "transaction_id": f"TXN-{txn_id_counter:07d}",
                    "account_id": acc_id,
                    "customer_id": c_id,
                    "branch_id": b_id,
                    "transaction_date": (account_end_dt - timedelta(days=2)).isoformat(),
                    "transaction_type": "Withdrawal",
                    "amount": drain_amount,
                    "balance_after": round(current_balance, 2),
                    "channel": "ONLINE",
                    "status": "Completed",
                    "description": "Full Balance Outbound Transfer to External Bank",
                    "merchant_category": "Transfer",
                    "created_at": (account_end_dt - timedelta(days=2)).isoformat()
                })
                txn_id_counter += 1

            # Account record
            accounts_records.append({
                "account_id": acc_id,
                "account_number": acc_num,
                "customer_id": c_id,
                "type_id": type_id,
                "branch_id": b_id,
                "currency": "USD",
                "current_balance": round(current_balance, 2),
                "available_balance": round(max(0.0, current_balance - 50.0), 2),
                "average_balance_90d": round(current_balance * random.uniform(0.9, 1.2), 2),
                "account_status": "Closed" if is_churned else "Active",
                "open_date": open_dt.date().isoformat(),
                "close_date": cust["churn_date"] if is_churned else None,
                "is_primary": is_prim,
                "created_at": open_dt.isoformat(),
                "updated_at": end_date.isoformat()
            })

    return pd.DataFrame(accounts_records), pd.DataFrame(transactions_records), pd.DataFrame(customer_products_records)


def generate_loans(customers_df, products_df, n_loans=250):
    """Generates installment and mortgage loan portfolio."""
    records = []
    loan_products = products_df[products_df["category"] == "Loan"]["product_id"].tolist()
    cust_ids = customers_df[not customers_df["churn_flag"]]["customer_id"].tolist()

    for i in range(1, n_loans + 1):
        c_id = random.choice(cust_ids)
        p_id = random.choice(loan_products)
        if "MTG" in p_id:
            principal = round(random.uniform(220000.0, 650000.0), -2)
            term = 360
            rate = 6.85
        elif "AUTO" in p_id:
            principal = round(random.uniform(18000.0, 55000.0), -2)
            term = 60
            rate = 6.49
        else:
            principal = round(random.uniform(5000.0, 25000.0), -2)
            term = 36
            rate = 10.50

        # Amortization installment approximation
        r = (rate / 100.0) / 12.0
        installment = round(principal * (r * (1 + r)**term) / ((1 + r)**term - 1), 2)
        months_elapsed = random.randint(3, min(term - 1, 24))
        cur_balance = round(principal * max(0.2, (term - months_elapsed) / term), 2)

        start_dt = date(2026, 11, 1) - timedelta(days=months_elapsed * 30)
        end_dt = start_dt + timedelta(days=term * 30)

        records.append({
            "loan_id": f"LN-{i:05d}",
            "loan_number": f"LOAN-{random.randint(10000, 99999)}-{i:04d}",
            "customer_id": c_id,
            "product_id": p_id,
            "principal_amount": principal,
            "current_balance": cur_balance,
            "interest_rate_pct": rate,
            "term_months": term,
            "monthly_installment": installment,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "status": "Current" if random.random() < 0.94 else "Delinquent",
            "delinquency_days": 0 if random.random() < 0.94 else random.choice([30, 60, 90]),
            "created_at": datetime.combine(start_dt, datetime.min.time()).isoformat()
        })
    return pd.DataFrame(records)


def generate_interactions_and_complaints(customers_df):
    """Generates customer service logs and complaints."""
    interaction_records = []
    complaint_records = []

    int_id_counter = 1
    cmp_id_counter = 1
    channels = ["Branch", "Phone", "Mobile App", "Web Chat", "Email"]
    categories = ["Fees", "Card Declined", "Digital Outage", "Customer Service", "Loan Processing", "Wire Delay"]

    for _, cust in customers_df.iterrows():
        c_id = cust["customer_id"]
        is_churned = cust["churn_flag"]

        # Churned customers have 3x more interactions and negative complaints
        n_ints = random.randint(1, 4) if not is_churned else random.randint(2, 6)

        for _ in range(n_ints):
            days_ago = random.randint(5, 300)
            int_date = datetime(2026, 11, 1) - timedelta(days=days_ago)
            sentiment = "Neutral"
            if is_churned and random.random() < 0.65:
                sentiment = "Negative"
            elif random.random() < 0.35:
                sentiment = "Positive"

            interaction_records.append({
                "interaction_id": f"INT-{int_id_counter:06d}",
                "customer_id": c_id,
                "interaction_date": int_date.isoformat(),
                "channel": random.choice(channels),
                "interaction_type": "Account Inquiry" if sentiment != "Negative" else "Dispute / Issue Escalation",
                "sentiment": sentiment,
                "summary": f"Customer called regarding {random.choice(categories).lower()} inquiry.",
                "agent_id": f"AGT-{random.randint(10, 99)}",
                "created_at": int_date.isoformat()
            })
            int_id_counter += 1

        # Complaints
        has_complaint = (is_churned and random.random() < 0.55) or (not is_churned and random.random() < 0.12)
        if has_complaint:
            days_ago = random.randint(15, 180)
            cmp_date = datetime(2026, 11, 1) - timedelta(days=days_ago)
            res_days = random.randint(2, 25)
            is_resolved = not is_churned or random.random() < 0.30

            complaint_records.append({
                "complaint_id": f"CMP-{cmp_id_counter:05d}",
                "customer_id": c_id,
                "category": random.choice(categories),
                "priority": "High" if is_churned else random.choice(["Low", "Medium", "High"]),
                "status": "Resolved" if is_resolved else "Open",
                "resolution_days": res_days if is_resolved else None,
                "description": "Customer reported dissatisfaction regarding unexpected fee or mobile connectivity.",
                "logged_date": cmp_date.isoformat(),
                "resolved_date": (cmp_date + timedelta(days=res_days)).isoformat() if is_resolved else None,
                "created_at": cmp_date.isoformat()
            })
            cmp_id_counter += 1

    return pd.DataFrame(interaction_records), pd.DataFrame(complaint_records)


def generate_campaigns_and_responses(customers_df):
    """Generates marketing campaigns, assignments, and response attribution."""
    campaigns = [
        {"campaign_id": "CMP-2026-Q1-RET", "campaign_name": "Q1 Win-Back & Retention Nudge", "campaign_code": "RET_Q1", "objective": "Retention", "target_segment": "At Risk", "start_date": "2026-01-15", "end_date": "2026-03-31", "budget": 45000.0, "channel": "RM Call", "status": "Completed"},
        {"campaign_id": "CMP-2026-Q2-DEP", "campaign_name": "Q2 High-Yield CD Spring Boost", "campaign_code": "DEP_Q2", "objective": "Deposit Growth", "target_segment": "Affluent", "start_date": "2026-04-01", "end_date": "2026-06-30", "budget": 60000.0, "channel": "Email", "status": "Completed"},
        {"campaign_id": "CMP-2026-Q3-CRD", "campaign_name": "Q3 Platinum Card Upgrade Wave", "campaign_code": "CRD_Q3", "objective": "Cross-Sell", "target_segment": "Young Professional", "start_date": "2026-07-01", "end_date": "2026-09-30", "budget": 35000.0, "channel": "Mobile Push", "status": "Completed"},
        {"campaign_id": "CMP-2026-Q4-AUT", "campaign_name": "Fall Auto Refinance Blitz", "campaign_code": "AUT_Q4", "objective": "Cross-Sell", "target_segment": "Mass Retail", "start_date": "2026-10-01", "end_date": "2026-11-15", "budget": 40000.0, "channel": "SMS", "status": "Active"},
        {"campaign_id": "CMP-2026-VIP-WLT", "campaign_name": "Private Wealth Advisory Invitations", "campaign_code": "VIP_WLT", "objective": "Retention", "target_segment": "High Net Worth", "start_date": "2026-02-01", "end_date": "2026-10-31", "budget": 80000.0, "channel": "Direct Mail", "status": "Completed"},
    ]
    camp_df = pd.DataFrame(campaigns)
    camp_df["created_at"] = datetime(2026, 1, 1, 9, 0, 0).isoformat()

    assignments = []
    responses = []
    asg_id_counter = 1
    resp_id_counter = 1

    cust_ids = customers_df["customer_id"].tolist()

    for _, c in camp_df.iterrows():
        c_id = c["campaign_id"]
        # Sample 150-250 customers per campaign
        sample_size = random.randint(140, 220)
        target_cohort = random.sample(cust_ids, min(sample_size, len(cust_ids)))

        for cust_id in target_cohort:
            asg_id = f"ASG-{asg_id_counter:06d}"
            asg_id_counter += 1
            start_dt = datetime.fromisoformat(c["start_date"])
            contact_dt = start_dt + timedelta(days=random.randint(1, 20))

            assignments.append({
                "assignment_id": asg_id,
                "campaign_id": c_id,
                "customer_id": cust_id,
                "assigned_date": c["start_date"],
                "contacted": True,
                "contacted_date": contact_dt.isoformat(),
                "created_at": start_dt.isoformat()
            })

            # Response and conversion
            responded = random.random() < 0.28  # 28% response rate
            converted = responded and (random.random() < 0.42)  # ~12% overall conversion
            resp_dt = contact_dt + timedelta(days=random.randint(1, 10))
            conv_dt = resp_dt + timedelta(days=random.randint(1, 7)) if converted else None
            attr_rev = round(random.uniform(450.0, 3200.0), 2) if converted else 0.0

            responses.append({
                "response_id": f"RES-{resp_id_counter:06d}",
                "assignment_id": asg_id,
                "response_date": resp_dt.isoformat(),
                "responded": responded,
                "converted": converted,
                "conversion_date": conv_dt.isoformat() if conv_dt else None,
                "attributed_revenue": attr_rev,
                "notes": "Client accepted high-yield promotional offer." if converted else ("Declined offer." if responded else "No response."),
                "created_at": resp_dt.isoformat()
            })
            resp_id_counter += 1

    return camp_df, pd.DataFrame(assignments), pd.DataFrame(responses)


def generate_all_synthetic_data(n_customers=1000):
    """Coordinates generation and export of all synthetic entities."""
    print(f"[*] Generating BankSight synthetic banking datasets (Target: {n_customers} customers)...")

    branches_df = generate_branches(n_branches=10)
    rms_df = generate_relationship_managers(branches_df, n_rms=25)
    account_types_df = generate_account_types()
    products_df = generate_products()

    customers_df = generate_customers(branches_df, rms_df, n_customers=n_customers)
    accounts_df, txns_df, cust_products_df = generate_accounts_and_transactions(customers_df, account_types_df, branches_df)
    loans_df = generate_loans(customers_df, products_df, n_loans=int(n_customers * 0.25))
    interactions_df, complaints_df = generate_interactions_and_complaints(customers_df)
    campaigns_df, assignments_df, responses_df = generate_campaigns_and_responses(customers_df)

    dataset_map = {
        "branches.csv": branches_df,
        "relationship_managers.csv": rms_df,
        "account_types.csv": account_types_df,
        "products.csv": products_df,
        "customers.csv": customers_df,
        "accounts.csv": accounts_df,
        "transactions.csv": txns_df,
        "customer_products.csv": cust_products_df,
        "loans.csv": loans_df,
        "customer_interactions.csv": interactions_df,
        "complaints.csv": complaints_df,
        "campaigns.csv": campaigns_df,
        "campaign_assignments.csv": assignments_df,
        "campaign_responses.csv": responses_df,
    }

    print("[+] Writing synthetic CSV datasets to data/synthetic/...")
    for filename, df in dataset_map.items():
        file_path = OUTPUT_DIR / filename
        df.to_csv(file_path, index=False)
        print(f"    - {filename:30s} : {len(df):6d} records ({file_path.stat().st_size / 1024:.1f} KB)")

    print("[+] Synthetic dataset generation complete!")
    return dataset_map


if __name__ == "__main__":
    generate_all_synthetic_data(n_customers=1000)
