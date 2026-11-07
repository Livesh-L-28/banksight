"""
BankSight Institutional Multi-Tenant & Branch Scoping Policy Test Suite
Verifies Row-Level Security (RLS) enforcement and cross-branch isolation.
"""

import pytest
from backend.security.tenancy import BranchScopingPolicy, ScopingAccessViolation


def test_global_scope_evaluation():
    """Verifies that Admin, Executive, and Compliance roles enjoy global bank visibility."""
    admin_user = {"username": "admin", "role": "Admin", "branch_id": None}
    exec_user = {"username": "cbo", "role": "Executive", "branch_id": None}
    compliance_user = {"username": "compliance", "role": "ComplianceOfficer", "branch_id": None}
    branch_mgr = {"username": "bm1", "role": "BranchManager", "branch_id": "BR-001"}

    assert BranchScopingPolicy.is_global_scope(admin_user) is True
    assert BranchScopingPolicy.is_global_scope(exec_user) is True
    assert BranchScopingPolicy.is_global_scope(compliance_user) is True
    assert BranchScopingPolicy.is_global_scope(branch_mgr) is False


def test_branch_manager_scope_resolution():
    """Verifies that BranchManagers are confined to their assigned branch."""
    bm_user = {"username": "bm1", "role": "BranchManager", "branch_id": "BR-001"}

    # Permitted query within assigned branch
    effective = BranchScopingPolicy.resolve_effective_branch(bm_user, requested_branch_id=None)
    assert effective == "BR-001"

    effective_same = BranchScopingPolicy.resolve_effective_branch(bm_user, requested_branch_id="BR-001")
    assert effective_same == "BR-001"

    # Attempt to access another branch must raise ScopingAccessViolation
    with pytest.raises(ScopingAccessViolation):
        BranchScopingPolicy.resolve_effective_branch(bm_user, requested_branch_id="BR-002")


def test_admin_branch_scope_resolution():
    """Verifies that Admin can query any branch or aggregate all branches."""
    admin_user = {"username": "admin", "role": "Admin", "branch_id": None}

    # Query all branches
    effective_all = BranchScopingPolicy.resolve_effective_branch(admin_user, requested_branch_id=None)
    assert effective_all is None

    # Query specific branch
    effective_specific = BranchScopingPolicy.resolve_effective_branch(admin_user, requested_branch_id="BR-002")
    assert effective_specific == "BR-002"


def test_in_memory_customer_access_validation():
    """Verifies customer record access boundaries for Branch Managers and RMs."""
    bm_user = {"username": "bm1", "role": "BranchManager", "branch_id": "BR-001"}
    rm_user = {"username": "rm1", "role": "RelationshipManager", "branch_id": "BR-001", "rm_id": "RM-001"}
    admin_user = {"username": "admin", "role": "Admin"}

    cust_br1 = {"customer_id": "CUST-00001", "branch_id": "BR-001", "rm_id": "RM-001"}
    cust_br2 = {"customer_id": "CUST-00002", "branch_id": "BR-002", "rm_id": "RM-002"}

    # Branch Manager
    assert BranchScopingPolicy.can_access_customer(cust_br1, bm_user) is True
    assert BranchScopingPolicy.can_access_customer(cust_br2, bm_user) is False

    # Relationship Manager
    assert BranchScopingPolicy.can_access_customer(cust_br1, rm_user) is True
    assert BranchScopingPolicy.can_access_customer(cust_br2, rm_user) is False

    # Admin
    assert BranchScopingPolicy.can_access_customer(cust_br1, admin_user) is True
    assert BranchScopingPolicy.can_access_customer(cust_br2, admin_user) is True
