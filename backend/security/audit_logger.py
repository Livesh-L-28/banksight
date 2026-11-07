"""
BankSight Immutable WORM Audit Logger
Provides tamper-evident cryptographic hash-chained audit logging for regulatory compliance (SOX, BCBS 239).
"""

import os
import json
import uuid
import hashlib
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

AUDIT_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
AUDIT_LOG_PATH = AUDIT_LOG_DIR / "audit_trail.jsonl"


class ImmutableAuditLogger:
    """
    Appends audit events into a SHA-256 hash-chained JSON-Lines ledger.
    Thread-safe with atomic locking to prevent fork race conditions in concurrent execution.
    """

    def __init__(self, log_path: Path = AUDIT_LOG_PATH):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._last_hash = self._get_latest_hash()

    def _get_latest_hash(self) -> str:
        """Reads the hash of the latest entry or returns genesis hash."""
        if not self.log_path.exists() or os.path.getsize(self.log_path) == 0:
            return "0" * 64
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_record = json.loads(lines[-1].strip())
                    return last_record.get("record_hash", "0" * 64)
        except Exception:
            return "0" * 64
        return "0" * 64

    def log_event(
        self,
        user_id: str,
        role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        client_ip: str = "127.0.0.1",
        status: str = "SUCCESS"
    ) -> Dict[str, Any]:
        """
        Creates and persists a tamper-evident audit record.
        """
        event_id = f"EVT-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._lock:
            record_payload = {
                "event_id": event_id,
                "timestamp_utc": timestamp,
                "prev_hash": self._last_hash,
                "user_id": user_id,
                "role": role,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": details or {},
                "client_ip": client_ip,
                "status": status
            }

            # Compute SHA-256 cryptographic signature
            serialized = json.dumps(record_payload, sort_keys=True)
            record_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            record_payload["record_hash"] = record_hash

            # Atomic append to ledger
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record_payload) + "\n")
                f.flush()

            self._last_hash = record_hash
            return record_payload

    def read_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Returns the most recent audit records."""
        if not self.log_path.exists():
            return []
        records = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records[-limit:]

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verifies the cryptographic chain integrity of the audit log.
        Returns validation status and record count.
        """
        if not self.log_path.exists() or os.path.getsize(self.log_path) == 0:
            return {"valid": True, "count": 0, "message": "Log ledger is empty or newly initialized."}

        prev_hash = "0" * 64
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                recorded_hash = record.get("record_hash")
                expected_prev = record.get("prev_hash")

                if expected_prev != prev_hash:
                    return {
                        "valid": False,
                        "line": line_no,
                        "error": f"Hash chain broken at line {line_no}. Expected prev {prev_hash}, got {expected_prev}"
                    }

                # Recompute hash without record_hash field
                payload_copy = {k: v for k, v in record.items() if k != "record_hash"}
                computed_hash = hashlib.sha256(json.dumps(payload_copy, sort_keys=True).encode("utf-8")).hexdigest()

                if computed_hash != recorded_hash:
                    return {
                        "valid": False,
                        "line": line_no,
                        "error": f"Tampered record at line {line_no}. Expected {computed_hash}, got {recorded_hash}"
                    }

                prev_hash = recorded_hash
                count += 1

        return {"valid": True, "count": count, "message": f"Successfully verified {count} audit records. Zero tampering detected."}


# Global audit logger instance
audit_logger = ImmutableAuditLogger()

