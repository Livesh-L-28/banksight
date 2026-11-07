"""
BankSight Dynamic Retention Concession Pricing Optimizer
Algorithmic pricing engine balancing customer retention uplift against concession cost
to determine the net-margin-maximizing retention incentive package.
"""

from typing import Dict, Any, List, Optional
from analytics.clv.uplift_engine import CustomerLifetimeValueEngine
from backend.database.connection import get_db_context
from backend.models import Customer, Account, ChurnPrediction


class ConcessionPricingOptimizer:
    """
    Evaluates candidate concessions and identifies the profit-maximizing retention offer.
    """

    STANDARD_OFFERS = [
        {
            "offer_id": "OFFER_NO_INCENTIVE",
            "offer_name": "Standard RM Advisory Check-In",
            "action_type": "Proactive Consultation",
            "cost_type": "FIXED",
            "annual_cost_usd": 0.0,
            "rate_adjustment_bps": 0,
            "retention_uplift_pct": 0.0,
            "description": "Standard relationship manager consultation without financial concessions."
        },
        {
            "offer_id": "OFFER_FEE_WAIVER",
            "offer_name": "Annual Maintenance & Wire Fee Waiver",
            "action_type": "Fee Concession",
            "cost_type": "FIXED",
            "annual_cost_usd": 72.0,
            "rate_adjustment_bps": 0,
            "retention_uplift_pct": 0.12,
            "description": "12-month waiver of account maintenance, ATM, and outgoing wire transaction fees."
        },
        {
            "offer_id": "OFFER_CD_BOOST_25BPS",
            "offer_name": "Premier High-Yield Deposit +25 bps Bonus",
            "action_type": "Deposit Rate Boost",
            "cost_type": "VARIABLE_BALANCE",
            "variable_rate_pct": 0.0025,  # 25 bps
            "rate_adjustment_bps": 25,
            "retention_uplift_pct": 0.22,
            "description": "Special 25 bps rate enhancement on 12-month Certificates of Deposit or Money Market accounts."
        },
        {
            "offer_id": "OFFER_CD_BOOST_50BPS",
            "offer_name": "Executive Relationship +50 bps Rate Match",
            "action_type": "Deposit Rate Boost",
            "cost_type": "VARIABLE_BALANCE",
            "variable_rate_pct": 0.0050,  # 50 bps
            "rate_adjustment_bps": 50,
            "retention_uplift_pct": 0.35,
            "description": "Competitive commercial rate matching granting +50 bps on core depository funds."
        },
        {
            "offer_id": "OFFER_LOAN_DISCOUNT_25BPS",
            "offer_name": "Consumer Credit Facility 25 bps Rate Relief",
            "action_type": "Lending Concession",
            "cost_type": "FIXED",
            "annual_cost_usd": 175.0,
            "rate_adjustment_bps": 25,
            "retention_uplift_pct": 0.16,
            "description": "Interest rate discount on existing mortgage, HELOC, or personal loan facility."
        },
        {
            "offer_id": "OFFER_PREMIER_UPGRADE",
            "offer_name": "Private Wealth Tier Upgrade & Dedicated Advisor",
            "action_type": "Service Upgrade",
            "cost_type": "FIXED",
            "annual_cost_usd": 150.0,
            "rate_adjustment_bps": 0,
            "retention_uplift_pct": 0.28,
            "description": "Complimentary upgrade to Private Wealth tier with waived advisory fees and dedicated planner."
        }
    ]

    @classmethod
    def evaluate_customer_offers(
        cls,
        total_balance: float,
        churn_probability: float,
        annual_income: float = 65000.0,
        loan_count: int = 0,
        custom_offers: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates candidate retention offers against customer financial profile and calculates
        expected net profit, ROI, and four-eyes regulatory flags.
        """
        clv_info = CustomerLifetimeValueEngine.calculate_customer_clv(
            total_balance=total_balance,
            churn_probability=churn_probability,
            annual_income=annual_income,
            loan_count=loan_count
        )

        potential_clv = clv_info["potential_36m_clv"]
        max_cap = clv_info["max_allowable_concession_usd"]
        baseline_retention_prob = max(0.02, 1.0 - churn_probability)
        baseline_expected_margin = baseline_retention_prob * potential_clv

        offers_to_evaluate = custom_offers or cls.STANDARD_OFFERS
        evaluated_offers = []

        for o in offers_to_evaluate:
            # Calculate annual cost
            if o.get("cost_type") == "VARIABLE_BALANCE":
                annual_cost = round(max(total_balance, 0.0) * o.get("variable_rate_pct", 0.0025), 2)
            else:
                annual_cost = round(float(o.get("annual_cost_usd", 0.0)), 2)

            rate_bps = int(o.get("rate_adjustment_bps", 0))
            uplift_pct = float(o.get("retention_uplift_pct", 0.0))

            # Uplifted retention probability
            p_retain_with_offer = min(0.98, baseline_retention_prob + uplift_pct)
            expected_gross_margin = round(p_retain_with_offer * potential_clv, 2)
            expected_net_margin = round(expected_gross_margin - annual_cost, 2)
            net_value_added = round(expected_net_margin - baseline_expected_margin, 2)

            # ROI calculation
            if annual_cost > 0.0:
                roi_pct = round((net_value_added / annual_cost) * 100.0, 1)
            else:
                roi_pct = 0.0

            # Governance flags
            within_cap = annual_cost <= max_cap or annual_cost == 0.0
            requires_four_eyes = annual_cost > 500.0 or rate_bps >= 50

            evaluated_offers.append({
                "offer_id": o["offer_id"],
                "offer_name": o["offer_name"],
                "action_type": o.get("action_type", "Concession"),
                "annual_cost_usd": annual_cost,
                "rate_adjustment_bps": rate_bps,
                "uplifted_retention_probability": round(p_retain_with_offer, 4),
                "expected_gross_margin_usd": expected_gross_margin,
                "expected_net_margin_usd": expected_net_margin,
                "net_value_added_usd": net_value_added,
                "roi_pct": roi_pct,
                "within_allowable_cap": within_cap,
                "requires_four_eyes_approval": requires_four_eyes,
                "description": o.get("description", "")
            })

        # Rank offers by Expected Net Margin among those within allowable cap
        eligible_offers = [o for o in evaluated_offers if o["within_allowable_cap"]]
        if not eligible_offers:
            eligible_offers = [evaluated_offers[0]]  # Default to no incentive

        optimal_offer = max(eligible_offers, key=lambda x: x["expected_net_margin_usd"])

        # Sort all evaluated offers by net value added descending
        ranked_offers = sorted(evaluated_offers, key=lambda x: x["expected_net_margin_usd"], reverse=True)

        return {
            "customer_profile": {
                "total_balance": round(total_balance, 2),
                "churn_probability": round(churn_probability, 4),
                "potential_36m_clv": potential_clv,
                "max_allowable_concession_usd": max_cap,
                "retention_quadrant": clv_info["retention_quadrant"]
            },
            "baseline_metrics": {
                "baseline_retention_prob": round(baseline_retention_prob, 4),
                "baseline_expected_margin_usd": round(baseline_expected_margin, 2)
            },
            "optimal_recommendation": {
                "offer_id": optimal_offer["offer_id"],
                "offer_name": optimal_offer["offer_name"],
                "annual_cost_usd": optimal_offer["annual_cost_usd"],
                "rate_adjustment_bps": optimal_offer["rate_adjustment_bps"],
                "projected_retention_probability": optimal_offer["uplifted_retention_probability"],
                "expected_net_gain_usd": optimal_offer["net_value_added_usd"],
                "roi_pct": optimal_offer["roi_pct"],
                "requires_four_eyes_approval": optimal_offer["requires_four_eyes_approval"],
                "rationale": (
                    f"Optimal choice: Generates ${optimal_offer['net_value_added_usd']:,.2f} in expected net value added "
                    f"at {optimal_offer['roi_pct']:.1f}% ROI while strictly respecting the ${max_cap:,.2f} concession limit."
                )
            },
            "evaluated_offers": ranked_offers
        }

    @classmethod
    def optimize_for_customer_id(cls, customer_id: str) -> Dict[str, Any]:
        """Loads customer details from database and runs concession pricing optimization."""
        with get_db_context() as session:
            cust = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not cust:
                return {"error": f"Customer '{customer_id}' not found."}

            accounts = cust.accounts or []
            total_bal = sum(a.current_balance for a in accounts)

            pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
            churn_prob = pred.churn_probability if pred else (0.85 if cust.churn_flag else 0.12)
            loan_cnt = len(cust.loans or [])

            result = cls.evaluate_customer_offers(
                total_balance=total_bal,
                churn_probability=churn_prob,
                annual_income=cust.annual_income or 65000.0,
                loan_count=loan_cnt
            )
            result["customer_profile"]["customer_id"] = cust.customer_id
            result["customer_profile"]["customer_name"] = f"{cust.first_name} {cust.last_name}"
            result["customer_profile"]["branch_id"] = cust.branch_id
            return result

