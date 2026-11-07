"""
BankSight Branch Performance & Regional Benchmarking Repository
Ranks branches, computes regional aggregates, and identifies underperforming units.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class BranchRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_branches(self) -> List[Dict[str, Any]]:
        """Returns list of all active branches."""
        sql = "SELECT branch_id, branch_name, branch_code, city, state, region FROM branches WHERE is_active = 1 ORDER BY branch_name"
        rows = self.session.execute(text(sql)).fetchall()
        return [
            {
                "branch_id": r[0],
                "branch_name": r[1],
                "branch_code": r[2],
                "city": r[3],
                "state": r[4],
                "region": r[5]
            }
            for r in rows
        ]

    def get_branch_rankings(self) -> List[Dict[str, Any]]:
        """Calculates comprehensive branch performance metrics and rankings."""
        sql = """
        SELECT
            b.branch_id,
            b.branch_name,
            b.city,
            b.state,
            b.region,
            COUNT(DISTINCT c.customer_id) as total_customers,
            SUM(CASE WHEN c.churn_flag = 1 THEN 1 ELSE 0 END) as churned_customers,
            ROUND(CAST(SUM(CASE WHEN c.churn_flag = 1 THEN 1 ELSE 0 END) AS FLOAT) /
                  NULLIF(COUNT(DISTINCT c.customer_id), 0) * 100, 2) as churn_rate_pct,
            COALESCE(SUM(a.current_balance), 0.0) as total_deposits,
            ROUND(COALESCE(AVG(a.current_balance), 0.0), 2) as avg_balance_per_acc,
            COUNT(DISTINCT t.transaction_id) as total_txns
        FROM branches b
        LEFT JOIN customers c ON b.branch_id = c.branch_id
        LEFT JOIN accounts a ON c.customer_id = a.customer_id
        LEFT JOIN transactions t ON a.account_id = t.account_id
        GROUP BY b.branch_id, b.branch_name, b.city, b.state, b.region
        ORDER BY total_deposits DESC
        """
        rows = self.session.execute(text(sql)).fetchall()

        rankings = []
        for idx, r in enumerate(rows, 1):
            tot_cust = int(r[5] or 0)
            churn_pct = float(r[7] or 0.0)
            tot_dep = round(float(r[8] or 0.0), 2)

            # Performance flag
            status = "Optimal"
            if churn_pct > 20.0 or tot_cust < 50:
                status = "Underperforming"
            elif tot_dep > 5000000.0:
                status = "Star Performer"

            rankings.append({
                "rank": idx,
                "branch_id": r[0],
                "branch_name": r[1],
                "city": r[2],
                "state": r[3],
                "region": r[4],
                "total_customers": tot_cust,
                "churned_customers": int(r[6] or 0),
                "churn_rate_pct": churn_pct,
                "total_deposits": tot_dep,
                "avg_balance_per_account": float(r[9] or 0.0),
                "total_transactions": int(r[10] or 0),
                "performance_tier": status
            })
        return rankings

    def get_regional_summary(self) -> List[Dict[str, Any]]:
        """Aggregates banking performance across geographic regions."""
        sql = """
        SELECT
            b.region,
            COUNT(DISTINCT b.branch_id) as branch_count,
            COUNT(DISTINCT c.customer_id) as customer_count,
            COALESCE(SUM(a.current_balance), 0.0) as regional_deposits,
            ROUND(CAST(SUM(CASE WHEN c.churn_flag = 1 THEN 1 ELSE 0 END) AS FLOAT) /
                  NULLIF(COUNT(DISTINCT c.customer_id), 0) * 100, 2) as regional_churn_pct
        FROM branches b
        LEFT JOIN customers c ON b.branch_id = c.branch_id
        LEFT JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY b.region
        ORDER BY regional_deposits DESC
        """
        rows = self.session.execute(text(sql)).fetchall()
        return [
            {
                "region": r[0],
                "branch_count": int(r[1] or 0),
                "customer_count": int(r[2] or 0),
                "regional_deposits": round(float(r[3] or 0.0), 2),
                "regional_churn_pct": float(r[4] or 0.0)
            }
            for r in rows
        ]
