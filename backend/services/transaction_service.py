"""
BankSight Transaction Analytics Service
Orchestrates channel distribution, spending trends, dormant account detection, and reconciliation audits.
"""

from typing import Dict, Any, List, Optional
from backend.database.connection import get_db_context
from backend.repositories.transaction_repo import TransactionRepository


class TransactionService:
    def get_channel_analytics(self, branch_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Retrieves volume and count distribution across transaction channels."""
        with get_db_context() as session:
            repo = TransactionRepository(session)
            return repo.get_channel_distribution(branch_ids)

    def get_spending_breakdown(self) -> List[Dict[str, Any]]:
        """Retrieves spending category aggregates."""
        with get_db_context() as session:
            repo = TransactionRepository(session)
            return repo.get_spending_by_category()

    def get_dormant_accounts(self, days_threshold: int = 90) -> List[Dict[str, Any]]:
        """Retrieves accounts with no debit activity for >90 days."""
        with get_db_context() as session:
            repo = TransactionRepository(session)
            return repo.get_dormant_accounts(days_threshold)

    def run_reconciliation(self) -> Dict[str, Any]:
        """Runs transaction ledger balance and duplicate reconciliation audit."""
        with get_db_context() as session:
            repo = TransactionRepository(session)
            return repo.run_reconciliation_audit()

