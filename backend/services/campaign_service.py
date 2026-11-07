"""
BankSight Campaign Analytics Service
Coordinates campaign performance tracking, revenue attribution, ROI, and cost-per-acquisition.
"""

from typing import Dict, Any, List
from backend.database.connection import get_db_context
from backend.repositories.campaign_repo import CampaignRepository


class CampaignService:
    def get_campaign_performance(self) -> List[Dict[str, Any]]:
        """Retrieves performance metrics, conversion rates, and ROI across all marketing campaigns."""
        with get_db_context() as session:
            repo = CampaignRepository(session)
            return repo.get_campaign_analytics()

