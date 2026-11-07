"""
BankSight Relationship Manager AI Copilot
Synthesizes Customer 360 intelligence into actionable pre-meeting briefing dossiers,
talking points, and personalized retention outreach communications.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class RMCopilotService:
    """
    Generates tailored Relationship Manager meeting briefings and retention outreach copy.
    Operates with zero external API dependencies using an enterprise banking prompt synthesis engine.
    """

    @classmethod
    def generate_meeting_briefing(
        cls,
        customer_dossier: Dict[str, Any],
        actor_name: Optional[str] = "Relationship Manager"
    ) -> Dict[str, Any]:
        """
        Synthesizes full customer dossier into an executive meeting brief and talking points.
        """
        cust_id = customer_dossier.get("customer_id", "Unknown")
        full_name = customer_dossier.get("full_name") or f"{customer_dossier.get('first_name', '')} {customer_dossier.get('last_name', '')}".strip() or "Valued Client"
        tenure_months = customer_dossier.get("tenure_months", 12)
        tenure_years = round(tenure_months / 12, 1)
        total_balance = customer_dossier.get("total_balance", 0.0)
        risk_cat = customer_dossier.get("churn_risk_category", "Medium Risk")
        prob = customer_dossier.get("churn_probability", 0.35)
        segment = customer_dossier.get("customer_segment", "Standard")
        complaints = customer_dossier.get("complaints", [])
        accounts = customer_dossier.get("accounts", [])
        occupation = customer_dossier.get("occupation", "Professional")

        # 1. Sentiment & Risk Diagnosis
        if len(complaints) > 0:
            sentiment = "Frustrated & Friction-Sensitive"
            sentiment_summary = (
                f"{full_name} has experienced operational friction with {len(complaints)} service complaint(s) logged. "
                f"Attrition risk is elevated ({prob:.1%}) due to dissatisfaction with issue resolution speed."
            )
        elif total_balance > 100000.0:
            sentiment = "High-Net-Worth & Yield-Conscious"
            sentiment_summary = (
                f"{full_name} is a high-value client with ${total_balance:,.2f} in deposits. Risk is driven by competitive "
                f"rate-shopping in the commercial banking market rather than operational dissatisfaction."
            )
        elif prob >= 0.70:
            sentiment = "Disengaged & Flight-Risk"
            sentiment_summary = (
                f"{full_name} has shown sharp drops in transaction frequency and digital banking activity. Immediate "
                f"intervention is required to prevent imminent account closure."
            )
        else:
            sentiment = "Stable but Under-Engaged"
            sentiment_summary = (
                f"{full_name} has been with the bank for {tenure_years} years with moderate transactional cadence. "
                f"Opportunity exists to deepen relationship through product cross-selling."
            )

        # 2. Key Attrition Signals
        signals: List[str] = []
        if len(complaints) > 0:
            signals.append(f"Recent Complaint: '{complaints[0].get('subject', 'Service Issue')}' status {complaints[0].get('status', 'Open')}")
        if total_balance < 1000.0:
            signals.append(f"Depleted Liquidity: Total balance has dropped to ${total_balance:,.2f}")
        if prob >= 0.50:
            signals.append(f"Predictive Model Flag: Attrition probability estimated at {prob:.1%}")
        if len(accounts) <= 1:
            signals.append("Low Product Depth: Single-account relationship increases vulnerability to competitor offers")
        if not signals:
            signals.append("Steady transactional cadence; periodic rate-sensitivity monitoring advised")

        # 3. Talking Points (Do's and Don'ts)
        dos: List[str] = []
        donts: List[str] = []

        if len(complaints) > 0:
            dos.append("Lead with accountability: Acknowledge the recent service issue upfront before discussing products.")
            dos.append("Offer concrete remediation: Confirm the issue was resolved and offer a courtesy account fee waiver.")
            donts.append("Do NOT attempt an aggressive sales pitch before resolving lingering operational frustration.")
        else:
            dos.append("Anchor on relationship tenure: Thank them for their loyalty over the past years.")
            dos.append("Present value-oriented savings options: Discuss high-yield deposit or premium wealth tier eligibility.")
            donts.append("Do NOT quote generic brochure rates; present tailored relationship-pricing brackets.")

        dos.append("Ask open-ended questions regarding upcoming business or family financial milestones.")
        donts.append("Do NOT bring up internal machine learning risk scores or churn classification flags during conversation.")

        # 4. Recommended Concession Strategy
        if total_balance >= 50000.0:
            strategy = {
                "primary_offer": "Premier High-Yield Savings Upgrade",
                "incentive_value": "$450 annual yield differential",
                "interest_rate_bonus": "+0.45% APY bonus for 12 months",
                "fee_waiver": "Waive all wire transfer and maintenance fees",
                "approval_required": "Standard RM Discretion"
            }
        elif len(complaints) > 0:
            strategy = {
                "primary_offer": "Courtesy Service Remediation Credit",
                "incentive_value": "$150 courtesy credit + 6-month fee waiver",
                "interest_rate_bonus": "N/A",
                "fee_waiver": "Immediate waiver of monthly maintenance fees",
                "approval_required": "Standard RM Discretion"
            }
        else:
            strategy = {
                "primary_offer": "Relationship Rewards Checking Tier",
                "incentive_value": "$100 direct deposit welcome incentive",
                "interest_rate_bonus": "+0.25% on 6-month CD ladder",
                "fee_waiver": "Complimentary premier debit card",
                "approval_required": "Standard RM Discretion"
            }

        # 5. Personalized Outreach Email / Letter Draft
        email_draft = f"""Subject: Dedicated Relationship Review — BankSight & {full_name}

Dear {customer_dossier.get('first_name', full_name)},

I hope this message finds you well. As your assigned Senior Relationship Manager at BankSight, I regularly review our clients' portfolios to ensure our accounts and financial services are continuing to support your goals.

Having partnered with you over the past {tenure_years} years, we truly value your continued trust. I would welcome the opportunity to connect for a brief 15-minute conversation this week to review your relationship benefits, explore our newly updated relationship-tier interest rates, and ensure all your day-to-day banking needs are running seamlessly.

Please let me know if Thursday at 10:30 AM or Friday at 2:00 PM works for a quick phone check-in or virtual meeting. Alternatively, you may reply with a time that best fits your calendar.

Warm regards,

{actor_name}
Senior Relationship Manager
BankSight Institutional Banking Group
"""

        return {
            "customer_id": cust_id,
            "customer_name": full_name,
            "generated_at": datetime.now().isoformat(),
            "tenure_summary": f"{tenure_years} years ({tenure_months} months)",
            "customer_segment": segment,
            "occupation": occupation,
            "churn_probability": prob,
            "risk_category": risk_cat,
            "sentiment_diagnosis": sentiment,
            "executive_summary": sentiment_summary,
            "key_attrition_signals": signals,
            "talking_points_dos": dos,
            "talking_points_donts": donts,
            "recommended_concession_strategy": strategy,
            "email_draft": email_draft,
            "recommended_meeting_duration": "15 to 20 minutes (Virtual or Phone)"
        }

