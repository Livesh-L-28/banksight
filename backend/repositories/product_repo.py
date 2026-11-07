"""
BankSight Product Intelligence & Cross-Selling Repository
Calculates product penetration, holdings, and rule-based cross-sell opportunities.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_product_portfolio(self) -> List[Dict[str, Any]]:
        """Calculates product penetration and active enrollment across product catalog."""
        sql = """
        SELECT
            p.product_id,
            p.product_code,
            p.product_name,
            p.category,
            p.interest_rate_pct,
            p.annual_fee,
            COUNT(DISTINCT cp.customer_id) as enrolled_customers,
            (SELECT COUNT(*) FROM customers) as total_customers
        FROM products p
        LEFT JOIN customer_products cp ON p.product_id = cp.product_id AND cp.status = 'Active'
        GROUP BY p.product_id, p.product_code, p.product_name, p.category, p.interest_rate_pct, p.annual_fee
        ORDER BY enrolled_customers DESC
        """
        rows = self.session.execute(text(sql)).fetchall()

        portfolio = []
        for r in rows:
            enrolled = int(r[6] or 0)
            tot_cust = int(r[7] or 1)
            pen_pct = round((enrolled / max(tot_cust, 1)) * 100, 2)
            portfolio.append({
                "product_id": r[0],
                "product_code": r[1],
                "product_name": r[2],
                "category": r[3],
                "interest_rate_pct": float(r[4] or 0.0),
                "annual_fee": float(r[5] or 0.0),
                "enrolled_customers": enrolled,
                "penetration_rate_pct": pen_pct
            })
        return portfolio

    def get_cross_sell_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identifies high-propensity cross-sell opportunities based on transparent financial rules.
        """
        session = self.session
        opportunities = []

        # Opportunity 1: High Balance Checking without Fixed Deposit -> Recommend 1-Year CD
        cd_rule_sql = """
        SELECT
            c.customer_id,
            c.first_name || ' ' || c.last_name as customer_name,
            c.annual_income,
            SUM(a.current_balance) as total_deposit_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        WHERE c.customer_status = 'Active'
        GROUP BY c.customer_id, customer_name, c.annual_income
        HAVING total_deposit_balance > 12000.0
           AND c.customer_id NOT IN (
               SELECT cp.customer_id FROM customer_products cp
               WHERE cp.product_id = 'PRD-CD-01' AND cp.status = 'Active'
           )
        ORDER BY total_deposit_balance DESC
        LIMIT 25;
        """
        cd_rows = session.execute(text(cd_rule_sql)).fetchall()
        for r in cd_rows:
            opportunities.append({
                "customer_id": r[0],
                "customer_name": r[1],
                "annual_income": float(r[2]),
                "current_balance": round(float(r[3]), 2),
                "recommended_product": "1-Year Fixed Deposit (5.00% APY)",
                "opportunity_type": "Surplus Liquidity Lock-In",
                "rationale": f"Client holds ${float(r[3]):,.2f} in liquid deposits without high-yield term investment."
            })

        # Opportunity 2: High Income without Platinum Card -> Recommend Platinum Card
        card_rule_sql = """
        SELECT
            c.customer_id,
            c.first_name || ' ' || c.last_name as customer_name,
            c.annual_income,
            c.credit_score
        FROM customers c
        WHERE c.customer_status = 'Active'
          AND c.annual_income > 85000.0
          AND c.credit_score >= 720
          AND c.customer_id NOT IN (
              SELECT cp.customer_id FROM customer_products cp
              WHERE cp.product_id = 'PRD-CRD-01' AND cp.status = 'Active'
          )
        ORDER BY c.annual_income DESC
        LIMIT 25;
        """
        card_rows = session.execute(text(card_rule_sql)).fetchall()
        for r in card_rows:
            opportunities.append({
                "customer_id": r[0],
                "customer_name": r[1],
                "annual_income": float(r[2]),
                "current_balance": 0.0,
                "recommended_product": "Platinum Rewards Credit Card",
                "opportunity_type": "Premium Card Cross-Sell",
                "rationale": f"High income (${float(r[2]):,.0f}) and prime credit score ({r[3]}) without premium rewards."
            })

        return opportunities
