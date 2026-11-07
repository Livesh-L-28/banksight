"""
BankSight Customer Lifetime Value (CLV) & Uplift Modeling Engine
Calculates discounted Net Present Value (NPV) cash flows over 12 and 36 months,
evaluates retention treatment effects, and assigns customers to Uplift Quadrants:
1. Persuadables (High value at risk, high incentive responsiveness)
2. Sure Things (High value, low churn risk, no costly incentive needed)
3. Lost Causes (Defecting regardless of intervention, avoid wasteful concessions)
4. Sleeping Dogs (Low balance, outreach may trigger dormant account closure)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from backend.database.connection import get_db_context
from backend.models import Customer, ChurnPrediction


class CustomerLifetimeValueEngine:
    """
    Computes discounted cash flow CLV and retention uplift economics.
    """

    DEFAULT_DISCOUNT_RATE = 0.08  # 8.0% annual weighted average cost of capital (WACC)
    NET_INTEREST_MARGIN = 0.022   # 220 bps net interest margin on core depository balances
    ANNUAL_FEE_INCOME = 72.0      # Base transaction, debit, and maintenance fee run-rate

    @classmethod
    def calculate_customer_clv(
        cls,
        total_balance: float,
        churn_probability: float,
        annual_income: float = 65000.0,
        loan_count: int = 0,
        discount_rate: float = DEFAULT_DISCOUNT_RATE
    ) -> Dict[str, Any]:
        """
        Calculates 12-month and 36-month discounted CLV based on net interest margin,
        fee run-rate, and survival decay.
        """
        annual_deposit_nim = max(total_balance, 0.0) * cls.NET_INTEREST_MARGIN
        annual_loan_spread = loan_count * 350.0  # Estimated net margin per credit facility
        annual_gross_revenue = annual_deposit_nim + annual_loan_spread + cls.ANNUAL_FEE_INCOME

        # 3-Year Potential Present Value if 100% retained
        pv_factor_3y = (1 / ((1 + discount_rate) ** 1)) + (1 / ((1 + discount_rate) ** 2)) + (1 / ((1 + discount_rate) ** 3))
        potential_36m_clv = round(annual_gross_revenue * pv_factor_3y, 2)

        # Annual retention survival probabilities under current churn decay
        p_stay_y1 = max(0.02, 1.0 - churn_probability)
        p_stay_y2 = p_stay_y1 * max(0.05, 1.0 - (churn_probability * 0.8))
        p_stay_y3 = p_stay_y2 * max(0.10, 1.0 - (churn_probability * 0.6))

        # Discounted Cash Flows (NPV)
        cf_y1 = (annual_gross_revenue * p_stay_y1) / ((1 + discount_rate) ** 1)
        cf_y2 = (annual_gross_revenue * p_stay_y2) / ((1 + discount_rate) ** 2)
        cf_y3 = (annual_gross_revenue * p_stay_y3) / ((1 + discount_rate) ** 3)

        clv_12m = round(cf_y1, 2)
        clv_36m = round(cf_y1 + cf_y2 + cf_y3, 2)
        clv_at_risk = round(max(0.0, potential_36m_clv - clv_36m), 2)

        # High Value Criteria: substantial depository balance or meaningful fee/loan run rate
        is_high_value = (total_balance >= 5000.0 or annual_gross_revenue >= 180.0 or potential_36m_clv >= 500.0)

        # Uplift Quadrant Assignment
        if is_high_value:
            if churn_probability > 0.80:
                quadrant = "Lost Causes"
                quadrant_badge = "⚠️ High Churn / Cap Concessions"
                treatment_strategy = "Relationship has severe defect risk. Limit concessions to standard service remediation."
                max_allowable_concession = min(50.0, round(potential_36m_clv * 0.02, 2))
            elif churn_probability >= 0.05:
                quadrant = "Persuadables"
                quadrant_badge = "🎯 High Priority Retention"
                treatment_strategy = "Deploy aggressive tailored concession (fee waiver, CD rate boost). High expected ROI."
                max_allowable_concession = min(round(potential_36m_clv * 0.12, 2), 2500.0)
            else:
                quadrant = "Sure Things"
                quadrant_badge = "💎 Core Wealth / Protect"
                treatment_strategy = "Customer is loyal and highly profitable. Do not grant costly concessions; focus on relationship reviews."
                max_allowable_concession = 0.0
        else:
            if churn_probability > 0.80:
                quadrant = "Lost Causes"
                quadrant_badge = "⚠️ High Churn / Cap Concessions"
                treatment_strategy = "Relationship has severe defect risk. Defection imminent with low recovery potential."
                max_allowable_concession = 0.0
            else:
                quadrant = "Sleeping Dogs"
                quadrant_badge = "💤 Low Margin / Passive Care"
                treatment_strategy = "Low balance or low engagement. Avoid disruptive sales outreach; maintain passive digital service."
                max_allowable_concession = 0.0

        return {
            "total_balance": round(total_balance, 2),
            "annual_gross_revenue": round(annual_gross_revenue, 2),
            "churn_probability": round(churn_probability, 4),
            "potential_36m_clv": potential_36m_clv,
            "clv_12m_npv": clv_12m,
            "clv_36m_npv": clv_36m,
            "clv_at_risk_usd": clv_at_risk,
            "retention_quadrant": quadrant,
            "quadrant_badge": quadrant_badge,
            "treatment_strategy": treatment_strategy,
            "max_allowable_concession_usd": max_allowable_concession
        }

    @classmethod
    def evaluate_portfolio_clv(cls) -> Dict[str, Any]:
        """
        Executes fleet-wide CLV and Uplift categorization across all active customers in the database.
        """
        with get_db_context() as session:
            # Join customers with accounts and churn predictions
            customers = session.query(Customer).all()
            if not customers:
                return {"error": "No customers found in database"}

            records = []
            for c in customers:
                tot_bal = sum(a.current_balance for a in c.accounts) if c.accounts else 0.0
                pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == c.customer_id).first()
                churn_prob = pred.churn_probability if pred else (0.85 if c.churn_flag else 0.12)

                clv_data = cls.calculate_customer_clv(
                    total_balance=tot_bal,
                    churn_probability=churn_prob,
                    annual_income=c.annual_income or 65000.0,
                    loan_count=len(c.loans) if c.loans else 0
                )
                records.append({
                    "customer_id": c.customer_id,
                    "customer_name": f"{c.first_name} {c.last_name}",
                    "branch_id": c.branch_id,
                    "customer_segment": c.customer_segment,
                    **clv_data
                })

        df = pd.DataFrame(records)
        total_36m_clv = float(df["clv_36m_npv"].sum())
        clv_at_risk = float(df[df["churn_probability"] >= 0.05]["clv_at_risk_usd"].sum())

        quadrant_summary = df["retention_quadrant"].value_counts().to_dict()
        persuadables_clv = float(df[df["retention_quadrant"] == "Persuadables"]["clv_36m_npv"].sum())

        return {
            "total_customers": len(df),
            "portfolio_36m_clv_usd": round(total_36m_clv, 2),
            "clv_at_risk_usd": round(clv_at_risk, 2),
            "persuadables_clv_usd": round(persuadables_clv, 2),
            "quadrant_distribution": quadrant_summary,
            "customer_sample": df.head(100).to_dict(orient="records"),
            "full_dataframe": df
        }
