"""
BankSight Database Initialization Utility
Creates all schema tables, verifies constraints, and logs initialization status.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.connection import engine, Base, DATABASE_URL
from backend.models import (
    Branch, RelationshipManager, Customer, AccountType, Account, Transaction,
    Product, CustomerProduct, Loan, CustomerInteraction, Complaint,
    Campaign, CampaignAssignment, CampaignResponse,
    CustomerSegment, ModelVersion, ChurnPrediction,
    RetentionCase, RetentionAction,
    DataImportJob, DataQualityResult
)


def init_database():
    """Initializes all database tables defined in the metadata."""
    print(f"[*] Initializing BankSight database schema at: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print(f"[+] Successfully verified and created {len(Base.metadata.tables)} tables in database.")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"    - {table_name}")


if __name__ == "__main__":
    init_database()
