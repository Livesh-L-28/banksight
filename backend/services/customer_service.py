"""
BankSight Customer 360 Service
Coordinates customer search, profile retrieval, account holdings, and timeline aggregation.
"""

from typing import List, Dict, Any, Optional
from backend.database.connection import get_db_context
from backend.repositories.customer_repo import CustomerRepository


class CustomerService:
    def search_customers(
        self,
        search_query: Optional[str] = None,
        branch_id: Optional[str] = None,
        segment: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Searches customer records with filters and pagination."""
        with get_db_context() as session:
            repo = CustomerRepository(session)
            return repo.search_customers(search_query, branch_id, segment, status, limit, offset)

    def get_customer_dossier(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves comprehensive Customer 360 intelligence dossier."""
        with get_db_context() as session:
            repo = CustomerRepository(session)
            return repo.get_customer_dossier(customer_id)
