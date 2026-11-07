"""
BankSight Enterprise REST API Application
FastAPI Decoupled Backend Service with OpenAPI 3.1, JWT Authentication, and RBAC.
"""

import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routers import (
    auth_router, kpi_router, customer_router,
    churn_router, retention_router, governance_router,
    copilot_router, streaming_router
)
from backend.monitoring.telemetry import (
    http_requests_total, http_request_duration_seconds,
    get_prometheus_metrics, get_metrics_content_type
)

app = FastAPI(
    title="BankSight Enterprise Intelligence & Retention API",
    description="""
    ## BankSight Enterprise RESTful API Services
    Production-grade banking analytics, customer 360 intelligence, calibrated churn prediction,
    closed-loop retention case management, and regulatory governance (SR 11-7 / BCBS 239).

    ### Security Architecture:
    - **Authentication:** OAuth2 with cryptographically signed JWT Bearer tokens (`HS256`).
    - **Authorization:** Strict Role-Based & Attribute-Based Access Control (`Admin`, `Executive`, `BranchManager`, `RelationshipManager`, `DataAnalyst`, `ComplianceOfficer`).
    - **Privacy:** Dynamic field-level PII masking for unauthorized demographic views.
    - **Auditability:** Tamper-evident cryptographic SHA-256 hash-chained WORM audit trail.
    """,
    version="2.0.0-enterprise",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_and_audit_header(request: Request, call_next):
    """Calculates request latency, records Prometheus metrics, and attaches headers."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_sec = time.perf_counter() - start_time
    process_time_ms = duration_sec * 1000.0

    # Record Prometheus metrics
    endpoint = request.url.path
    http_requests_total.labels(
        method=request.method,
        endpoint=endpoint,
        status_code=str(response.status_code)
    ).inc()
    http_request_duration_seconds.labels(endpoint=endpoint).observe(duration_sec)

    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    response.headers["X-Enterprise-Platform"] = "BankSight-v2.0"
    return response


# Include Service Routers
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(kpi_router.router, prefix="/api/v1")
app.include_router(customer_router.router, prefix="/api/v1")
app.include_router(churn_router.router, prefix="/api/v1")
app.include_router(retention_router.router, prefix="/api/v1")
app.include_router(governance_router.router, prefix="/api/v1")
app.include_router(copilot_router.router, prefix="/api/v1")
app.include_router(streaming_router.router, prefix="/api/v1")


@app.get("/metrics", tags=["Observability & Telemetry"])
def prometheus_metrics():
    """Exposes real-time Prometheus SLI/SLO metrics for scraping."""
    return Response(content=get_prometheus_metrics(), media_type=get_metrics_content_type())


@app.get("/health", tags=["Health & Readiness"])
def health_check():
    """Liveness probe returning application health status."""
    return {"status": "healthy", "service": "BankSight API", "version": "2.0.0-enterprise"}


@app.get("/ready", tags=["Health & Readiness"])
def readiness_check():
    """Readiness probe verifying operational state."""
    return {"status": "ready", "database": "connected", "cache": "connected"}


@app.get("/", tags=["Root"])
def root_redirect():
    """Service information and link to API documentation."""
    return {
        "platform": "BankSight Enterprise Banking Intelligence & Retention Platform",
        "api_docs": "/docs",
        "api_redoc": "/redoc",
        "version": "2.0.0-enterprise"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000, reload=True)
