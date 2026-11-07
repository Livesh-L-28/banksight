"""
BankSight Prometheus Telemetry & Metrics Exporter
Exposes real-time SLI/SLO metrics for operational monitoring, latency tracking, and regulatory alerting.
"""

from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
)

# 1. API Throughput & Latency Metrics
http_requests_total = Counter(
    "banksight_http_requests_total",
    "Total HTTP requests handled by the BankSight platform",
    ["method", "endpoint", "status_code"]
)

http_request_duration_seconds = Histogram(
    "banksight_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

# 2. Machine Learning Inference Telemetry
churn_inference_latency_seconds = Histogram(
    "banksight_churn_inference_latency_seconds",
    "Real-time machine learning churn scoring latency in seconds",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5)
)

# 3. Operational Retention Pipeline Gauges
active_retention_cases_gauge = Gauge(
    "banksight_active_retention_cases",
    "Number of active retention cases currently open across branches",
    ["priority", "status"]
)

# 4. Streaming Attrition Triggers
capital_flight_alerts_total = Counter(
    "banksight_capital_flight_alerts_total",
    "Total real-time capital flight detection events triggered"
)


def get_prometheus_metrics() -> bytes:
    """Exports all registered metrics in standard Prometheus text exposition format."""
    return generate_latest()


def get_metrics_content_type() -> str:
    """Returns official Prometheus content type header."""
    return CONTENT_TYPE_LATEST
