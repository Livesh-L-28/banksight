"""
BankSight Database Seeding & Ingestion Utility
Loads generated synthetic CSV datasets into the relational database with foreign key integrity.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date
import pandas as pd
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.connection import engine, get_db_context
from backend.models import (
    Branch, RelationshipManager, Customer, AccountType, Account, Transaction,
    Product, CustomerProduct, Loan, CustomerInteraction, Complaint,
    Campaign, CampaignAssignment, CampaignResponse
)

SYNTHETIC_DIR = Path(__file__).resolve().parent.parent / "data" / "synthetic"


def parse_date(val):
    if pd.isna(val) or val is None or val == "":
        return None
    if isinstance(val, date):
        return val
    return date.fromisoformat(str(val).split("T")[0])


def parse_datetime(val):
    if pd.isna(val) or val is None or val == "":
        return None
    if isinstance(val, datetime):
        return val
    s = str(val).replace("Z", "")
    return datetime.fromisoformat(s)


def seed_database():
    """Seeds the relational database from synthetic CSV files."""
    print("[*] Starting BankSight database ingestion from data/synthetic/...")
    start_time = datetime.now()

    with get_db_context() as session:
        # Disable foreign keys temporarily if truncating
        print("[-] Clearing existing records to ensure idempotent seed...")
        for tbl in [
            "campaign_responses", "campaign_assignments", "campaigns",
            "complaints", "customer_interactions", "loans", "customer_products",
            "transactions", "accounts", "customers", "relationship_managers",
            "branches", "account_types", "products"
        ]:
            session.execute(text(f"DELETE FROM {tbl};"))
        session.commit()

        # 1. Branches
        branches_df = pd.read_csv(SYNTHETIC_DIR / "branches.csv")
        for _, r in branches_df.iterrows():
            session.add(Branch(
                branch_id=r["branch_id"],
                branch_name=r["branch_name"],
                branch_code=r["branch_code"],
                address=r["address"],
                city=r["city"],
                state=r["state"],
                postal_code=str(r["postal_code"]),
                region=r["region"],
                is_active=bool(r["is_active"]),
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(branches_df)} branches.")

        # 2. Relationship Managers
        rms_df = pd.read_csv(SYNTHETIC_DIR / "relationship_managers.csv")
        for _, r in rms_df.iterrows():
            session.add(RelationshipManager(
                rm_id=r["rm_id"],
                branch_id=r["branch_id"],
                first_name=r["first_name"],
                last_name=r["last_name"],
                email=r["email"],
                phone=r["phone"],
                portfolio_size=int(r["portfolio_size"]),
                is_active=bool(r["is_active"]),
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(rms_df)} relationship managers.")

        # 3. Account Types
        act_types_df = pd.read_csv(SYNTHETIC_DIR / "account_types.csv")
        for _, r in act_types_df.iterrows():
            session.add(AccountType(
                type_id=r["type_id"],
                type_name=r["type_name"],
                category=r["category"],
                interest_rate_pct=float(r["interest_rate_pct"]),
                monthly_fee=float(r["monthly_fee"]),
                minimum_balance_req=float(r["minimum_balance_req"]),
                description=r.get("description", None),
                created_at=datetime.utcnow()
            ))
        session.commit()
        print(f"[+] Loaded {len(act_types_df)} account types.")

        # 4. Products
        prods_df = pd.read_csv(SYNTHETIC_DIR / "products.csv")
        for _, r in prods_df.iterrows():
            session.add(Product(
                product_id=r["product_id"],
                product_code=r["product_code"],
                product_name=r["product_name"],
                category=r["category"],
                annual_fee=float(r["annual_fee"]),
                interest_rate_pct=float(r["interest_rate_pct"]),
                target_segment=r.get("target_segment", None),
                is_active=bool(r["is_active"]),
                created_at=datetime.utcnow()
            ))
        session.commit()
        print(f"[+] Loaded {len(prods_df)} products.")

        # 5. Customers
        custs_df = pd.read_csv(SYNTHETIC_DIR / "customers.csv")
        for _, r in custs_df.iterrows():
            session.add(Customer(
                customer_id=r["customer_id"],
                first_name=r["first_name"],
                last_name=r["last_name"],
                email=r["email"],
                phone=r["phone"],
                date_of_birth=parse_date(r["date_of_birth"]),
                age=int(r["age"]),
                gender=r["gender"],
                occupation=r["occupation"],
                annual_income=float(r["annual_income"]),
                address=r["address"],
                city=r["city"],
                state=r["state"],
                postal_code=str(r["postal_code"]),
                country=r["country"],
                joining_date=parse_date(r["joining_date"]),
                customer_tenure_months=int(r["customer_tenure_months"]),
                customer_status=r["customer_status"],
                customer_segment=r["customer_segment"],
                branch_id=r["branch_id"],
                rm_id=r["rm_id"] if pd.notna(r["rm_id"]) else None,
                credit_score=int(r["credit_score"]) if pd.notna(r["credit_score"]) else None,
                kyc_verified=bool(r["kyc_verified"]),
                digital_banking_active=bool(r["digital_banking_active"]),
                mobile_banking_active=bool(r["mobile_banking_active"]),
                opt_in_marketing=bool(r["opt_in_marketing"]),
                churn_flag=bool(r["churn_flag"]),
                churn_date=parse_date(r["churn_date"]) if pd.notna(r["churn_date"]) else None,
                created_at=parse_datetime(r["created_at"]),
                updated_at=parse_datetime(r["updated_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(custs_df)} customers.")

        # 6. Accounts
        accs_df = pd.read_csv(SYNTHETIC_DIR / "accounts.csv")
        for _, r in accs_df.iterrows():
            session.add(Account(
                account_id=r["account_id"],
                account_number=r["account_number"],
                customer_id=r["customer_id"],
                type_id=r["type_id"],
                branch_id=r["branch_id"],
                currency=r["currency"],
                current_balance=float(r["current_balance"]),
                available_balance=float(r["available_balance"]),
                average_balance_90d=float(r["average_balance_90d"]),
                account_status=r["account_status"],
                open_date=parse_date(r["open_date"]),
                close_date=parse_date(r["close_date"]) if pd.notna(r["close_date"]) else None,
                is_primary=bool(r["is_primary"]),
                created_at=parse_datetime(r["created_at"]),
                updated_at=parse_datetime(r["updated_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(accs_df)} accounts.")

        # 7. Customer Products
        cp_df = pd.read_csv(SYNTHETIC_DIR / "customer_products.csv")
        for _, r in cp_df.iterrows():
            session.add(CustomerProduct(
                cust_prod_id=r["cust_prod_id"],
                customer_id=r["customer_id"],
                product_id=r["product_id"],
                enrollment_date=parse_date(r["enrollment_date"]),
                status=r["status"],
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(cp_df)} customer products.")

        # 8. Loans
        loans_df = pd.read_csv(SYNTHETIC_DIR / "loans.csv")
        for _, r in loans_df.iterrows():
            session.add(Loan(
                loan_id=r["loan_id"],
                loan_number=r["loan_number"],
                customer_id=r["customer_id"],
                product_id=r["product_id"],
                principal_amount=float(r["principal_amount"]),
                current_balance=float(r["current_balance"]),
                interest_rate_pct=float(r["interest_rate_pct"]),
                term_months=int(r["term_months"]),
                monthly_installment=float(r["monthly_installment"]),
                start_date=parse_date(r["start_date"]),
                end_date=parse_date(r["end_date"]),
                status=r["status"],
                delinquency_days=int(r["delinquency_days"]),
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(loans_df)} loans.")

        # 9. Customer Interactions
        ints_df = pd.read_csv(SYNTHETIC_DIR / "customer_interactions.csv")
        for _, r in ints_df.iterrows():
            session.add(CustomerInteraction(
                interaction_id=r["interaction_id"],
                customer_id=r["customer_id"],
                interaction_date=parse_datetime(r["interaction_date"]),
                channel=r["channel"],
                interaction_type=r["interaction_type"],
                sentiment=r["sentiment"],
                summary=r.get("summary", None),
                agent_id=r.get("agent_id", None),
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(ints_df)} customer interactions.")

        # 10. Complaints
        cmps_df = pd.read_csv(SYNTHETIC_DIR / "complaints.csv")
        for _, r in cmps_df.iterrows():
            session.add(Complaint(
                complaint_id=r["complaint_id"],
                customer_id=r["customer_id"],
                category=r["category"],
                priority=r["priority"],
                status=r["status"],
                resolution_days=int(r["resolution_days"]) if pd.notna(r["resolution_days"]) else None,
                description=r["description"],
                logged_date=parse_datetime(r["logged_date"]),
                resolved_date=parse_datetime(r["resolved_date"]) if pd.notna(r["resolved_date"]) else None,
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(cmps_df)} complaints.")

        # 11. Campaigns
        camps_df = pd.read_csv(SYNTHETIC_DIR / "campaigns.csv")
        for _, r in camps_df.iterrows():
            session.add(Campaign(
                campaign_id=r["campaign_id"],
                campaign_name=r["campaign_name"],
                campaign_code=r["campaign_code"],
                objective=r["objective"],
                target_segment=r["target_segment"],
                start_date=parse_date(r["start_date"]),
                end_date=parse_date(r["end_date"]),
                budget=float(r["budget"]),
                channel=r["channel"],
                status=r["status"],
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(camps_df)} campaigns.")

        # 12. Campaign Assignments
        asgs_df = pd.read_csv(SYNTHETIC_DIR / "campaign_assignments.csv")
        for _, r in asgs_df.iterrows():
            session.add(CampaignAssignment(
                assignment_id=r["assignment_id"],
                campaign_id=r["campaign_id"],
                customer_id=r["customer_id"],
                assigned_date=parse_date(r["assigned_date"]),
                contacted=bool(r["contacted"]),
                contacted_date=parse_datetime(r["contacted_date"]) if pd.notna(r["contacted_date"]) else None,
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(asgs_df)} campaign assignments.")

        # 13. Campaign Responses
        resps_df = pd.read_csv(SYNTHETIC_DIR / "campaign_responses.csv")
        for _, r in resps_df.iterrows():
            session.add(CampaignResponse(
                response_id=r["response_id"],
                assignment_id=r["assignment_id"],
                response_date=parse_datetime(r["response_date"]),
                responded=bool(r["responded"]),
                converted=bool(r["converted"]),
                conversion_date=parse_datetime(r["conversion_date"]) if pd.notna(r["conversion_date"]) else None,
                attributed_revenue=float(r["attributed_revenue"]),
                notes=r.get("notes", None),
                created_at=parse_datetime(r["created_at"])
            ))
        session.commit()
        print(f"[+] Loaded {len(resps_df)} campaign responses.")

        # 14. Transactions (batch insert using chunks for high throughput)
        txns_df = pd.read_csv(SYNTHETIC_DIR / "transactions.csv")
        chunk_size = 5000
        total_txns = len(txns_df)
        print(f"[-] Ingesting {total_txns} transactions in batches of {chunk_size}...")

        for start_idx in range(0, total_txns, chunk_size):
            chunk = txns_df.iloc[start_idx:start_idx + chunk_size]
            batch_objects = [
                Transaction(
                    transaction_id=r["transaction_id"],
                    account_id=r["account_id"],
                    customer_id=r["customer_id"],
                    branch_id=r["branch_id"],
                    transaction_date=parse_datetime(r["transaction_date"]),
                    transaction_type=r["transaction_type"],
                    amount=float(r["amount"]),
                    balance_after=float(r["balance_after"]),
                    channel=r["channel"],
                    status=r["status"],
                    description=r.get("description", None),
                    merchant_category=r.get("merchant_category", None),
                    created_at=parse_datetime(r["created_at"])
                )
                for _, r in chunk.iterrows()
            ]
            session.bulk_save_objects(batch_objects)
            session.commit()
            print(f"    - Ingested {min(start_idx + chunk_size, total_txns)} / {total_txns} transactions...")

        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"[+] Successfully seeded database with all 14 entity collections in {elapsed:.1f} seconds.")


if __name__ == "__main__":
    seed_database()

