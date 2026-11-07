"""
BankSight Distributed Tracing & W3C Trace Context Test Suite
Verifies W3C traceparent compliance, trace propagation, and HTTP header injection.
"""

from fastapi.testclient import TestClient
from backend.api.main import app
from backend.monitoring.tracing import DistributedTraceContext, TRACEPARENT_REGEX

client = TestClient(app)


def test_w3c_traceparent_parser_and_generator():
    """Verifies that DistributedTraceContext parses and formats compliant W3C headers."""
    # Test valid incoming traceparent
    valid_tp = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    trace_id, parent_id, flags = DistributedTraceContext.parse_traceparent(valid_tp)
    assert trace_id == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert parent_id == "00f067aa0ba902b7"
    assert flags == "01"

    # Test invalid / empty traceparent generates fresh valid W3C context
    tid, pid, flg = DistributedTraceContext.parse_traceparent(None)
    assert len(tid) == 32
    assert len(pid) == 16
    assert flg == "01"

    formatted = DistributedTraceContext.format_traceparent(tid, pid, flg)
    assert TRACEPARENT_REGEX.match(formatted) is not None


def test_http_distributed_trace_header_injection():
    """Verifies that API responses include W3C traceparent and correlation headers."""
    resp = client.get("/health")
    assert resp.status_code == 200

    assert "traceparent" in resp.headers
    assert "X-Trace-ID" in resp.headers
    assert "X-Span-ID" in resp.headers
    assert "X-Correlation-ID" in resp.headers

    # Verify W3C syntax format
    traceparent_val = resp.headers["traceparent"]
    match = TRACEPARENT_REGEX.match(traceparent_val)
    assert match is not None
    assert match.group(1) == resp.headers["X-Trace-ID"]
    assert match.group(2) == resp.headers["X-Span-ID"]


def test_http_distributed_trace_propagation():
    """Verifies that incoming W3C trace ID is preserved and propagated downstream."""
    custom_trace_id = "1234567890abcdef1234567890abcdef"
    custom_span_id = "fedcba0987654321"
    incoming_header = f"00-{custom_trace_id}-{custom_span_id}-01"

    resp = client.get("/health", headers={"traceparent": incoming_header, "X-Correlation-ID": "MY-CORR-123"})
    assert resp.status_code == 200

    # The trace_id must match the incoming trace_id
    assert resp.headers["X-Trace-ID"] == custom_trace_id
    assert resp.headers["X-Correlation-ID"] == "MY-CORR-123"
    assert resp.headers["traceparent"].startswith(f"00-{custom_trace_id}-")

