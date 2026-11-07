"""
BankSight Institutional Multi-Tenant & Branch Scoping Policy Engine
Enforces Row-Level Security (RLS) and Attribute-Based Access Control (ABAC)
across regional banking branches, portfolio managers, and regulatory roles.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Query


class ScopingAccessViolation(Exception):
    """Raised when an actor attempts to inspect or mutate records outside authorized scope."""
    pass


class BranchScopingPolicy:
    """
    Evaluates organizational boundary rules and clamps queries to authorized scopes.
    """

    GLOBAL_ROLES = {"Admin", "Executive", "ComplianceOfficer"}

    @classmethod
    def is_global_scope(cls, user: Dict[str, Any]) -> bool:
        """Determines if the user possesses bank-wide visibility."""
        role = user.get("role", "")
        return role in cls.GLOBAL_ROLES

    @classmethod
    def resolve_effective_branch(
        cls,
        user: Dict[str, Any],
        requested_branch_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Resolves the branch ID authorized for the given user.
        Raises ScopingAccessViolation if a branch-restricted user requests another branch.
        """
        role = user.get("role", "")
        user_branch = user.get("branch_id")

        if role == "BranchManager":
            if not user_branch:
                raise ScopingAccessViolation("BranchManager account has no assigned branch_id.")
            if requested_branch_id and requested_branch_id != user_branch and requested_branch_id != "All":
                raise ScopingAccessViolation(
                    f"BranchManager assigned to '{user_branch}' cannot access branch '{requested_branch_id}'."
                )
            return user_branch

        elif role == "RelationshipManager":
            if not user_branch:
                raise ScopingAccessViolation("RelationshipManager account has no assigned branch_id.")
            if requested_branch_id and requested_branch_id != user_branch:
                raise ScopingAccessViolation(
                    f"RelationshipManager assigned to '{user_branch}' cannot query branch '{requested_branch_id}'."
                )
            return user_branch

        # Global roles can query any branch or all branches
        return None if requested_branch_id in [None, "All"] else requested_branch_id

    @classmethod
    def scope_customer_query(cls, query: Query, user: Dict[str, Any], customer_model: Any) -> Query:
        """
        Applies row-level SQL filters based on user role and assigned scope.
        """
        role = user.get("role", "")

        if role == "BranchManager":
            branch_id = user.get("branch_id")
            if branch_id:
                return query.filter(customer_model.branch_id == branch_id)

        elif role == "RelationshipManager":
            rm_id = user.get("rm_id")
            if rm_id:
                return query.filter(customer_model.rm_id == rm_id)

        return query

    @classmethod
    def scope_retention_case_query(cls, query: Query, user: Dict[str, Any], case_model: Any, customer_model: Any) -> Query:
        """
        Applies row-level SQL filters for retention case workflows.
        """
        role = user.get("role", "")

        if role == "BranchManager":
            branch_id = user.get("branch_id")
            if branch_id:
                return query.join(customer_model, case_model.customer_id == customer_model.customer_id)\
                            .filter(customer_model.branch_id == branch_id)

        elif role == "RelationshipManager":
            rm_id = user.get("rm_id")
            if rm_id:
                return query.filter(case_model.rm_id == rm_id)

        return query

    @classmethod
    def can_access_customer(cls, customer_dict: Dict[str, Any], user: Dict[str, Any]) -> bool:
        """
        Validates in-memory access rights to a specific customer record.
        """
        if cls.is_global_scope(user) or user.get("role") == "DataAnalyst":
            return True

        role = user.get("role", "")
        if role == "BranchManager":
            return customer_dict.get("branch_id") == user.get("branch_id")
        elif role == "RelationshipManager":
            return customer_dict.get("rm_id") == user.get("rm_id")

        return False

