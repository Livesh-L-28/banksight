"""
BankSight Distributed Tracing & W3C Trace Context Engine
Implements W3C Trace Context standard (traceparent: 00-{trace_id}-{parent_id}-{flags})
for end-to-end distributed transaction observability across Core Banking and API Gateways.
"""

import os
import re
import secrets
from typing import Optional, Tuple
from contextvars import ContextVar

# ContextVars to store active distributed trace context for the current async/thread execution
_current_trace_id: ContextVar[Optional[str]] = ContextVar("current_trace_id", default=None)
_current_span_id: ContextVar[Optional[str]] = ContextVar("current_span_id", default=None)

# W3C traceparent regex: 00-{32 hex trace_id}-{16 hex parent_id}-{2 hex flags}
TRACEPARENT_REGEX = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")


class DistributedTraceContext:
    """
    Manages W3C Trace Context generation, propagation, and correlation across services.
    """

    @staticmethod
    def generate_trace_id() -> str:
        """Generates a standard 128-bit (32-character hex) trace ID."""
        return secrets.token_hex(16)

    @staticmethod
    def generate_span_id() -> str:
        """Generates a standard 64-bit (16-character hex) span ID."""
        return secrets.token_hex(8)

    @classmethod
    def parse_traceparent(cls, header_value: Optional[str]) -> Tuple[str, str, str]:
        """
        Parses incoming W3C 'traceparent' header or generates a fresh context if missing/invalid.
        Returns (trace_id, parent_id, flags).
        """
        if header_value:
            match = TRACEPARENT_REGEX.match(header_value.strip().lower())
            if match:
                trace_id, parent_id, flags = match.groups()
                # Verify non-zero trace_id and parent_id
                if trace_id != "0" * 32 and parent_id != "0" * 16:
                    return trace_id, parent_id, flags

        # Generate new trace context if absent or invalid
        new_trace_id = cls.generate_trace_id()
        new_span_id = cls.generate_span_id()
        return new_trace_id, new_span_id, "01"

    @classmethod
    def format_traceparent(cls, trace_id: str, span_id: str, flags: str = "01") -> str:
        """Formats W3C compliant traceparent string."""
        return f"00-{trace_id}-{span_id}-{flags}"

    @classmethod
    def set_active_trace(cls, trace_id: str, span_id: str) -> None:
        """Binds the active trace and span IDs to the current execution context."""
        _current_trace_id.set(trace_id)
        _current_span_id.set(span_id)

    @classmethod
    def get_active_trace_id(cls) -> str:
        """Returns the active trace ID or generates one if unassigned."""
        tid = _current_trace_id.get()
        if not tid:
            tid = cls.generate_trace_id()
            _current_trace_id.set(tid)
        return tid

    @classmethod
    def get_active_span_id(cls) -> str:
        """Returns the active span ID or generates one if unassigned."""
        sid = _current_span_id.get()
        if not sid:
            sid = cls.generate_span_id()
            _current_span_id.set(sid)
        return sid

