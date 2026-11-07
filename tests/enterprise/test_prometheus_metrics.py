"""
Enterprise Tests for SRE Observability & Prometheus Telemetry
"""

from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_prometheus_metrics_endpoint():
    """Validates the standard Prometheus exposition endpoint at /metrics."""
    # First make a normal API call to record metrics
    res_health = client.get("/health")
    assert res_health.status_code == 200

    # Scrape metrics
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    metrics_text = res_metrics.text

    # Verify key metrics are exposed in Prometheus format
    assert "banksight_http_requests_total" in metrics_text
    assert "banksight_http_request_duration_seconds" in metrics_text
    assert "banksight_churn_inference_latency_seconds" in metrics_text
    assert "banksight_capital_flight_alerts_total" in metrics_text
