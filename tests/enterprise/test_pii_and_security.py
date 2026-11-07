"""
Enterprise Security Tests: PII Masking, Field Encryption, and Immutable WORM Audit Chain
"""

import tempfile
import json
from pathlib import Path
from backend.security.pii_masker import PIIMasker
from backend.security.encryption import FieldEncryptionService
from backend.security.audit_logger import ImmutableAuditLogger


def test_pii_masking_rules():
    """Validates dynamic PII masking adheres to role-based privacy policies."""
    # DataAnalyst should see masked fields
    assert PIIMasker.mask_name("Eleanor Vance", role="DataAnalyst") == "E****** V****"
    assert PIIMasker.mask_email("eleanor.vance@example.com", role="DataAnalyst") == "e***e@example.com"
    assert PIIMasker.mask_phone("+1-555-987-6543", role="DataAnalyst") == "***-***-6543"
    assert PIIMasker.mask_account_number("ACC-0001928", role="DataAnalyst") == "ACC-****1928"

    # Admin and ComplianceOfficer should see unmasked fields
    assert PIIMasker.mask_name("Eleanor Vance", role="Admin") == "Eleanor Vance"
    assert PIIMasker.mask_email("eleanor.vance@example.com", role="ComplianceOfficer") == "eleanor.vance@example.com"
    assert PIIMasker.mask_phone("+1-555-987-6543", role="Admin") == "+1-555-987-6543"


def test_field_encryption_and_decryption():
    """Validates cryptographic field-level AES encryption at rest."""
    service = FieldEncryptionService()
    secret_text = "US-SSN-987-65-4321"

    ciphertext = service.encrypt(secret_text)
    assert ciphertext is not None
    assert ciphertext != secret_text
    assert len(ciphertext) > 20

    decrypted = service.decrypt(ciphertext)
    assert decrypted == secret_text


def test_immutable_audit_logger_hash_chain():
    """Validates WORM audit logging and cryptographic tamper-detection."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        log_file = Path(tmp_dir) / "test_audit.jsonl"
        logger = ImmutableAuditLogger(log_path=log_file)

        # Append 3 audit events
        logger.log_event("admin", "Admin", "VIEW_CUSTOMER", "CUSTOMER", "CUST-00001")
        logger.log_event("rm_alex", "RelationshipManager", "OFFER_PROPOSED", "RETENTION_CASE", "CASE-00010")
        logger.log_event("compliance", "ComplianceOfficer", "VERIFY_AUDIT", "SYSTEM", "ALL")

        # Integrity verification on clean log
        result = logger.verify_integrity()
        assert result["valid"] is True
        assert result["count"] == 3

        # Simulate adversarial log tampering (modifying an actor name on line 2)
        with open(log_file, "r") as f:
            lines = f.readlines()

        tampered_record = json.loads(lines[1])
        tampered_record["action"] = "UNAUTHORIZED_ALTERATION"
        lines[1] = json.dumps(tampered_record) + "\n"

        with open(log_file, "w") as f:
            f.writelines(lines)

        # Integrity verification must catch tampering
        tamper_check = logger.verify_integrity()
        assert tamper_check["valid"] is False
        assert "Tampered record at line 2" in tamper_check["error"]

