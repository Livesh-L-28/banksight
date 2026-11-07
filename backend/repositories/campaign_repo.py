"""
BankSight Campaign Intelligence & Marketing Attribution Repository
Calculates campaign reach, conversion, attributed revenue, ROI, and cost-per-acquisition.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text


class CampaignRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_campaign_analytics(self) -> List[Dict[str, Any]]:
        """Calculates performance and ROI metrics for all marketing campaigns."""
        sql = """
        SELECT
            cmp.campaign_id,
            cmp.campaign_name,
            cmp.campaign_code,
            cmp.objective,
            cmp.target_segment,
            cmp.channel,
            cmp.budget,
            cmp.status,
            COUNT(DISTINCT ca.assignment_id) as total_reach,
            SUM(CASE WHEN cr.responded = 1 THEN 1 ELSE 0 END) as total_responses,
            SUM(CASE WHEN cr.converted = 1 THEN 1 ELSE 0 END) as total_conversions,
            COALESCE(SUM(cr.attributed_revenue), 0.0) as total_attributed_revenue
        FROM campaigns cmp
        LEFT JOIN campaign_assignments ca ON cmp.campaign_id = ca.campaign_id
        LEFT JOIN campaign_responses cr ON ca.assignment_id = cr.assignment_id
        GROUP BY cmp.campaign_id, cmp.campaign_name, cmp.campaign_code, cmp.objective,
                 cmp.target_segment, cmp.channel, cmp.budget, cmp.status
        ORDER BY cmp.start_date DESC
        """
        rows = self.session.execute(text(sql)).fetchall()

        results = []
        for r in rows:
            reach = int(r[8] or 0)
            responses = int(r[9] or 0)
            conversions = int(r[10] or 0)
            budget = float(r[6] or 0.0)
            rev = float(r[11] or 0.0)

            resp_rate = round((responses / max(reach, 1)) * 100, 2)
            conv_rate = round((conversions / max(responses, 1)) * 100, 2) if responses > 0 else 0.0
            overall_conv = round((conversions / max(reach, 1)) * 100, 2)
            roi_pct = round(((rev - budget) / max(budget, 1.0)) * 100, 2)
            cpa = round(budget / max(conversions, 1), 2)

            results.append({
                "campaign_id": r[0],
                "campaign_name": r[1],
                "campaign_code": r[2],
                "objective": r[3],
                "target_segment": r[4],
                "channel": r[5],
                "budget": budget,
                "status": r[7],
                "reach": reach,
                "responses": responses,
                "conversions": conversions,
                "response_rate_pct": resp_rate,
                "conversion_rate_pct": conv_rate,
                "overall_conversion_pct": overall_conv,
                "attributed_revenue": round(rev, 2),
                "roi_pct": roi_pct,
                "cpa": cpa
            })
        return results
