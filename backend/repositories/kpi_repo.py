"""
BankSight Executive KPI Repository
Executes dynamic SQL calculations for all 15 core banking KPIs with multidimensional slicing.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date
from sqlalchemy import text, func, and_, or_, Integer
from sqlalchemy.orm import Session
from backend.models import (
    Customer, Account, Transaction, CampaignAssignment, CampaignResponse,
    ChurnPrediction, Branch, Product
)


class KPIRepository:
    def __init__(self, session: Session):
        self.session = session

    def calculate_executive_kpis(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        branch_ids: Optional[List[str]] = None,
        customer_segments: Optional[List[str]] = None,
        product_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Dynamically computes all 15 executive banking KPIs based on active filters.
        """
        session = self.session

        # Base customer query
        cust_query = session.query(Customer)
        if branch_ids:
            cust_query = cust_query.filter(Customer.branch_id.in_(branch_ids))
        if customer_segments:
            cust_query = cust_query.filter(Customer.customer_segment.in_(customer_segments))
        if start_date:
            cust_query = cust_query.filter(Customer.joining_date >= start_date)
        if end_date:
            cust_query = cust_query.filter(Customer.joining_date <= end_date)

        filtered_custs = cust_query.all()
        filtered_cust_ids = [c.customer_id for c in filtered_custs]

        if not filtered_cust_ids:
            return {
                "total_customers": 0,
                "active_customers": 0,
                "inactive_customers": 0,
                "new_customers": 0,
                "total_accounts": 0,
                "total_deposits": 0.0,
                "total_withdrawals": 0.0,
                "total_transaction_value": 0.0,
                "average_customer_balance": 0.0,
                "arpu": 0.0,
                "churn_rate_pct": 0.0,
                "retention_rate_pct": 100.0,
                "customer_lifetime_value": 0.0,
                "high_risk_customers": 0,
                "campaign_conversion_rate": 0.0
            }

        total_customers = len(filtered_cust_ids)
        churned_count = sum(1 for c in filtered_custs if c.churn_flag)
        active_customers = sum(1 for c in filtered_custs if c.customer_status == "Active" and not c.churn_flag)
        inactive_customers = total_customers - active_customers

        # New customers in last 90 days (relative to 2026-11-01)
        ref_date = date(2026, 11, 1)
        new_customers = sum(1 for c in filtered_custs if c.joining_date >= date(2026, 5, 1))

        churn_rate_pct = round((churned_count / total_customers) * 100, 2) if total_customers > 0 else 0.0
        retention_rate_pct = round(100.0 - churn_rate_pct, 2)

        # Accounts for these customers
        acc_query = session.query(Account).filter(Account.customer_id.in_(filtered_cust_ids))
        accounts = acc_query.all()
        total_accounts = len(accounts)
        total_portfolio_balance = sum(a.current_balance for a in accounts)
        avg_customer_balance = round(total_portfolio_balance / max(total_customers, 1), 2)

        # Transactions for these customers
        txn_query = session.query(
            Transaction.transaction_type,
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.transaction_id).label("txn_count")
        ).filter(Transaction.customer_id.in_(filtered_cust_ids))

        if start_date:
            txn_query = txn_query.filter(Transaction.transaction_date >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            txn_query = txn_query.filter(Transaction.transaction_date <= datetime.combine(end_date, datetime.max.time()))

        txn_summary = txn_query.group_by(Transaction.transaction_type).all()

        total_deposits = 0.0
        total_withdrawals = 0.0
        for row in txn_summary:
            if row.transaction_type == "Deposit":
                total_deposits = float(row.total_amount or 0.0)
            elif row.transaction_type in ["Withdrawal", "Payment"]:
                total_withdrawals += float(row.total_amount or 0.0)

        total_transaction_value = round(total_deposits + total_withdrawals, 2)

        # ARPU (Estimated 2.5% spread on average balance + $120 annual fee baseline)
        arpu = round(0.025 * avg_customer_balance + 120.0, 2)

        # Customer Lifetime Value (CLV = (ARPU * 0.75) / (churn_rate + 0.08))
        effective_churn = max(0.05, churn_rate_pct / 100.0)
        clv = round((arpu * 0.75) / (effective_churn + 0.08), 2)

        # High risk customers (from ChurnPrediction or simulated high probability)
        high_risk_query = session.query(func.count(ChurnPrediction.prediction_id)).filter(
            and_(
                ChurnPrediction.customer_id.in_(filtered_cust_ids),
                ChurnPrediction.risk_category == "High Risk"
            )
        )
        high_risk_count = high_risk_query.scalar() or 0
        if high_risk_count == 0 and churned_count > 0:
            # Fallback before ML pipeline runs: count inactive/churned customers
            high_risk_count = int(churned_count * 1.25)

        # Campaign conversion rate for filtered cohort
        camp_query = session.query(
            func.count(CampaignResponse.response_id).label("total_responses"),
            func.sum(func.cast(CampaignResponse.converted, Integer)).label("total_conversions")
        ).join(CampaignAssignment, CampaignResponse.assignment_id == CampaignAssignment.assignment_id)\
         .filter(CampaignAssignment.customer_id.in_(filtered_cust_ids))

        camp_res = camp_query.first()
        camp_responses = camp_res.total_responses or 0
        camp_conversions = camp_res.total_conversions or 0
        camp_conversion_rate = round((camp_conversions / max(camp_responses, 1)) * 100, 2) if camp_responses > 0 else 0.0

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "inactive_customers": inactive_customers,
            "new_customers": new_customers,
            "total_accounts": total_accounts,
            "total_deposits": round(total_deposits, 2),
            "total_withdrawals": round(total_withdrawals, 2),
            "total_transaction_value": total_transaction_value,
            "average_customer_balance": avg_customer_balance,
            "arpu": arpu,
            "churn_rate_pct": churn_rate_pct,
            "retention_rate_pct": retention_rate_pct,
            "customer_lifetime_value": clv,
            "high_risk_customers": high_risk_count,
            "campaign_conversion_rate": camp_conversion_rate
        }

    def get_monthly_transaction_trend(
        self,
        branch_ids: Optional[List[str]] = None,
        customer_segments: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Returns monthly deposit, withdrawal, and transaction volume trends."""
        session = self.session

        sql = """
        SELECT
            strftime('%Y-%m', t.transaction_date) as month,
            SUM(CASE WHEN t.transaction_type = 'Deposit' THEN t.amount ELSE 0 END) as deposits,
            SUM(CASE WHEN t.transaction_type IN ('Withdrawal', 'Payment') THEN t.amount ELSE 0 END) as withdrawals,
            COUNT(t.transaction_id) as txn_count
        FROM transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE 1=1
        """
        params = {}
        if branch_ids:
            placeholders = ", ".join([f":b_{i}" for i in range(len(branch_ids))])
            sql += f" AND c.branch_id IN ({placeholders})"
            for i, b_id in enumerate(branch_ids):
                params[f"b_{i}"] = b_id

        if customer_segments:
            placeholders = ", ".join([f":s_{i}" for i in range(len(customer_segments))])
            sql += f" AND c.customer_segment IN ({placeholders})"
            for i, s_val in enumerate(customer_segments):
                params[f"s_{i}"] = s_val

        sql += " GROUP BY strftime('%Y-%m', t.transaction_date) ORDER BY month ASC"

        rows = session.execute(text(sql), params).fetchall()
        return [
            {
                "month": r[0],
                "deposits": round(float(r[1] or 0.0), 2),
                "withdrawals": round(float(r[2] or 0.0), 2),
                "net_flow": round(float(r[1] or 0.0) - float(r[2] or 0.0), 2),
                "transaction_count": int(r[3] or 0)
            }
            for r in rows
        ]
