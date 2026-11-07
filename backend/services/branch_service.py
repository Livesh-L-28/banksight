"""
BankSight Branch Intelligence Service
Provides branch rankings, regional aggregation, and underperforming branch alerts.
"""

from typing import Dict, Any, List
from backend.database.connection import get_db_context
from backend.repositories.branch_repo import BranchRepository


class BranchService:
    def get_all_branches(self) -> List[Dict[str, Any]]:
        """Retrieves list of active branches for UI dropdowns."""
        with get_db_context() as session:
            repo = BranchRepository(session)
            return repo.get_all_branches()

    def get_branch_rankings(self) -> List[Dict[str, Any]]:
        """Retrieves ranked performance table for all branches."""
        with get_db_context() as session:
            repo = BranchRepository(session)
            return repo.get_branch_rankings()

    def get_regional_summary(self) -> List[Dict[str, Any]]:
        """Retrieves regional summary metrics."""
        with get_db_context() as session:
            repo = BranchRepository(session)
            return repo.get_regional_summary()

