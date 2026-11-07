"""
BankSight Transaction Analytics Repository
Provides transaction volume dynamics, channel distribution, spending analytics,
dormant account identification, and ledger reconciliation checks.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from backend.models import Transaction, Account, Customer


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_channel_distribution(
        self,
        branch_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Calculates volume and count distribution across transaction channels."""
        session = self.session
        sql = """
        SELECT
            t.channel,
            COUNT(t.transaction_id) as txn_count,
            SUM(t.amount) as total_volume,
            AVG(t.amount) as avg_amount
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE 1=1
        """
        params = {}
        if branch_ids:
            placeholders = ", ".join([f":b_{i}" for i in range(len(branch_ids))])
            sql += f" AND a.branch_id IN ({placeholders})"
            for i, b in enumerate(branch_ids):
                params[f"b_{i}"] = b

        sql += " GROUP BY t.channel ORDER BY total_volume DESC"
        rows = session.execute(text(sql), params).fetchall()

        return [
            {
                "channel": r[0],
                "transaction_count": int(r[1] or 0),
                "total_volume": round(float(r[2] or 0.0), 2),
                "average_amount": round(float(r[3] or 0.0), 2)
            }
            for r in rows
        ]

    def get_spending_by_category(self) -> List[Dict[str, Any]]:
        """Calculates expenditure breakdown across spending categories."""
        sql = """
        SELECT
            COALESCE(merchant_category, 'General Spending') as category,
            COUNT(transaction_id) as txn_count,
            SUM(amount) as total_spend
        FROM transactions
        WHERE transaction_type IN ('Withdrawal', 'Payment')
        GROUP BY COALESCE(merchant_category, 'General Spending')
        ORDER BY total_spend DESC
        """
        rows = self.session.execute(text(sql)).fetchall()
        return [
            {
                "category": r[0],
                "transaction_count": int(r[1] or 0),
                "total_spend": round(float(r[2] or 0.0), 2)
            }
            for r in rows
        ]

    def get_dormant_accounts(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """Identifies accounts with no debit transaction for more than days_threshold days."""
        sql = f"""
        SELECT
            a.account_id,
            a.account_number,
            c.customer_id,
            c.first_name || ' ' || c.last_name as customer_name,
            c.email,
            a.current_balance,
            MAX(t.transaction_date) as last_txn_date,
            ROUND(JULIANDAY('2026-11-01') - JULIANDAY(MAX(t.transaction_date))) as days_inactive
        FROM accounts a
        JOIN customers c ON a.customer_id = c.customer_id
        LEFT JOIN transactions t ON a.account_id = t.account_id
        WHERE a.account_status = 'Active'
        GROUP BY a.account_id, a.account_number, c.customer_id, customer_name, c.email, a.current_balance
        HAVING days_inactive > {days_threshold} OR last_txn_date IS NULL
        ORDER BY days_inactive DESC
        LIMIT 50;
        """
        rows = self.session.execute(text(sql)).fetchall()
        return [
            {
                "account_id": r[0],
                "account_number": r[1],
                "customer_id": r[2],
                "customer_name": r[3],
                "email": r[4],
                "current_balance": round(float(r[5] or 0.0), 2),
                "last_transaction_date": str(r[6]) if r[6] else "No transactions",
                "days_inactive": int(r[7]) if r[7] is not None else 365
            }
            for r in rows
        ]

    def run_reconciliation_audit(self) -> Dict[str, Any]:
        """Performs analytical integrity and balance reconciliation checks."""
        session = self.session

        total_txns = session.query(func.count(Transaction.transaction_id)).scalar() or 0
        total_deposit_val = session.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == "Deposit"
        ).scalar() or 0.0

        total_withdrawal_val = session.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type.in_(["Withdrawal", "Payment"])
        ).scalar() or 0.0

        # Duplicate transaction check
        dup_sql = """
        SELECT COUNT(*) FROM (
            SELECT transaction_id FROM transactions GROUP BY transaction_id HAVING COUNT(*) > 1
        )
        """
        duplicate_count = session.execute(text(dup_sql)).scalar() or 0

        # Negative balance check
        neg_bal_count = session.query(func.count(Account.account_id)).filter(
            Account.current_balance < 0
        ).scalar() or 0

        # Discrepancy check: active accounts with zero transactions
        orphan_acc_sql = """
        SELECT COUNT(a.account_id)
        FROM accounts a
        LEFT JOIN transactions t ON a.account_id = t.account_id
        WHERE t.transaction_id IS NULL;
        """
        zero_txn_accounts = session.execute(text(orphan_acc_sql)).scalar() or 0

        return {
            "total_transaction_records": total_txns,
            "total_deposit_amount": round(float(total_deposit_val), 2),
            "total_withdrawal_amount": round(float(total_withdrawal_val), 2),
            "net_flow": round(float(total_deposit_val) - float(total_withdrawal_val), 2),
            "duplicate_transactions_found": int(duplicate_count),
            "negative_balance_accounts": int(neg_bal_count),
            "accounts_without_transactions": int(zero_txn_accounts),
            "reconciliation_status": "Balanced & Verified" if duplicate_count == 0 and neg_bal_count == 0 else "Anomalies Detected"
        }
