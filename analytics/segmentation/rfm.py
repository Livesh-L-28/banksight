"""
BankSight RFM Customer Segmentation Module
Calculates Recency, Frequency, Monetary quintiles and assigns banking customer segment labels.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


class RFMSegmenter:
    def __init__(self):
        pass

    def compute_rfm_scores(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes RFM quantiles (1 to 5) and assigns standard banking segment labels.
        Recency: Lower days = Higher score (rank 5 is most recent).
        Frequency: Higher count = Higher score (rank 5 is most frequent).
        Monetary: Higher spend/balance = Higher score (rank 5 is highest value).
        """
        df = features_df.copy()

        # Recency score (inverted: rank 5 = lowest recency days)
        # Using qcut with duplicates='drop'
        df["r_score"] = pd.qcut(df["recency_days"].rank(method="first"), q=5, labels=[5, 4, 3, 2, 1]).astype(int)

        # Frequency score
        df["f_score"] = pd.qcut(df["txn_frequency_12m"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        # Monetary score (using total_balance + total_spend_12m)
        monetary_val = df["total_balance"] + df["total_spend_12m"]
        df["m_score"] = pd.qcut(monetary_val.rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)

        df["rfm_score"] = df["r_score"].astype(str) + df["f_score"].astype(str) + df["m_score"].astype(str)

        # Assign segments based on measured RFM criteria
        def assign_label(row):
            r, f, m = row["r_score"], row["f_score"], row["m_score"]
            if r >= 4 and f >= 4 and m >= 4:
                return "High Value"
            elif r >= 3 and f >= 3 and m >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2 and m >= 3:
                return "High Growth Potential"
            elif r >= 4 and f <= 2 and m <= 2:
                return "New Customers"
            elif r <= 2 and f >= 3 and m >= 3:
                return "At Risk"
            elif r <= 2 and f <= 2 and m <= 2:
                return "Dormant"
            elif r <= 2 and f <= 2 and m >= 3:
                return "Potential Loyalists"
            else:
                return "Low Engagement"

        df["rfm_segment"] = df.apply(assign_label, axis=1)
        return df

    def get_segment_recommendations(self, segment_label: str) -> Dict[str, Any]:
        """Returns empirical business action recommendations for an RFM segment."""
        playbooks = {
            "High Value": {
                "objective": "Protect & Expand Wealth",
                "recommended_actions": [
                    "Assign dedicated Senior Relationship Manager",
                    "Offer tailored Private Wealth & Family Office advisory",
                    "Provide preferential CD and Money Market rates (+0.50% APY)"
                ],
                "campaign_affinity": "Wealth Management & Concierge"
            },
            "Loyal Customers": {
                "objective": "Cross-Sell High-Margin Products",
                "recommended_actions": [
                    "Invite to Premium Rewards Credit Card program",
                    "Present pre-qualified Auto Refinance and Mortgage offers",
                    "Deliver quarterly customer appreciation loyalty perks"
                ],
                "campaign_affinity": "Cross-Sell Platinum Card"
            },
            "High Growth Potential": {
                "objective": "Nurture Account Velocity",
                "recommended_actions": [
                    "Promote automated recurring direct deposit savings",
                    "Deliver personalized financial wellness mobile insights",
                    "Incentivize bill-pay and digital wallet integration"
                ],
                "campaign_affinity": "Digital Banking Engagement"
            },
            "New Customers": {
                "objective": "Onboarding & Relationship Anchoring",
                "recommended_actions": [
                    "Send 30-day welcome concierge check-in",
                    "Provide step-by-step mobile banking tour",
                    "Offer $25 initial funding bonus upon 5 debit card transactions"
                ],
                "campaign_affinity": "Early Stage Onboarding"
            },
            "At Risk": {
                "objective": "Urgent Preemptive Retention",
                "recommended_actions": [
                    "Trigger automated outreach by Branch RM within 48 hours",
                    "Conduct root-cause diagnostic on recent fee disputes or balance drops",
                    "Propose 6-month fee waiver or APY retention boost"
                ],
                "campaign_affinity": "VIP Win-Back Nurture"
            },
            "Dormant": {
                "objective": "Cost-Effective Reactivation",
                "recommended_actions": [
                    "Send digital reactivation email with $10 survey incentive",
                    "Verify mailing address and customer contact preferences",
                    "Evaluate for statutory dormancy escheatment compliance"
                ],
                "campaign_affinity": "Re-engagement Push"
            },
            "Potential Loyalists": {
                "objective": "Deepen Primary Banking Relationship",
                "recommended_actions": [
                    "Offer incentive to switch primary payroll direct deposit",
                    "Present no-fee high-yield savings pairing",
                    "Invite to local financial literacy branch seminar"
                ],
                "campaign_affinity": "Direct Deposit Switch"
            },
            "Low Engagement": {
                "objective": "Drive Digital Adoption",
                "recommended_actions": [
                    "Promote contactless mobile tap-and-pay",
                    "Encourage e-statements to reduce maintenance overhead",
                    "Provide low-balance alert configuration"
                ],
                "campaign_affinity": "Mobile App Adoption"
            }
        }
        return playbooks.get(segment_label, {
            "objective": "General Relationship Maintenance",
            "recommended_actions": ["Conduct standard periodic review"],
            "campaign_affinity": "Standard Marketing"
        })
