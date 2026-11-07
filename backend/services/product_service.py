"""
BankSight Product Intelligence Service
Coordinates product penetration analysis and transparent cross-sell rule recommendations.
"""

from typing import Dict, Any, List
from backend.database.connection import get_db_context
from backend.repositories.product_repo import ProductRepository


class ProductService:
    def get_portfolio_penetration(self) -> List[Dict[str, Any]]:
        """Retrieves penetration rates across all catalog products."""
        with get_db_context() as session:
            repo = ProductRepository(session)
            return repo.get_product_portfolio()

    def get_cross_sell_leads(self) -> List[Dict[str, Any]]:
        """Retrieves eligible cross-sell candidates based on transparent banking rules."""
        with get_db_context() as session:
            repo = ProductRepository(session)
            return repo.get_cross_sell_opportunities()

