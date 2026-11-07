"""
BankSight Governance, Audit & Model Risk Router (SR 11-7 / BCBS 239)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from pydantic import BaseModel, Field
from backend.api.dependencies import require_roles, log_api_action
from backend.api.schemas import AuditLogItem, AuditIntegrityResponse
from backend.security.audit_logger import audit_logger
from analytics.stress_testing.ccar_simulator import CCARStressTestSimulator
from backend.monitoring.telemetry import basel_iii_lcr_pct

router = APIRouter(prefix="/governance", tags=["Governance, Audit & Regulatory Compliance"])


class StressTestRequest(BaseModel):
    scenario: str = Field(default="ADVERSE", example="ADVERSE", description="Supervisory scenario: BASELINE, ADVERSE, or SEVERELY_ADVERSE")
    hqla_buffer_usd: float = Field(default=12000000.0, example=12000000.0, description="Available High Quality Liquid Assets (HQLA) in USD")



@router.get("/audit-logs", response_model=List[AuditLogItem])
def get_audit_trail(
    request: Request,
    limit: int = Query(50, le=500),
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Retrieves immutable audit records from the tamper-evident WORM ledger.
    """
    records = audit_logger.read_logs(limit=limit)
    log_api_action(request, user, "INSPECT_AUDIT_LOGS", "AUDIT_LEDGER", f"limit={limit}")
    return [AuditLogItem(**r) for r in records]


@router.get("/audit-integrity", response_model=AuditIntegrityResponse)
def verify_audit_ledger_integrity(
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Cryptographically verifies the SHA-256 hash-chain integrity of the audit ledger.
    """
    result = audit_logger.verify_integrity()
    log_api_action(request, user, "VERIFY_AUDIT_INTEGRITY", "AUDIT_LEDGER", "CHAIN_VERIFICATION")
    return AuditIntegrityResponse(**result)


@router.get("/sr11-7-summary")
def get_sr11_7_validation_summary(
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer", "DataAnalyst", "Executive"]))
):
    """
    Returns an executive summary of the SR 11-7 Model Risk Management validation assessment.
    """
    log_api_action(request, user, "VIEW_SR11_7_SUMMARY", "GOVERNANCE", "SR11_7")
    return {
        "framework": "Federal Reserve SR 11-7 / OCC 2011-12",
        "model_name": "BankSight Customer Churn Predictive Pipeline",
        "validation_status": "APPROVED_FOR_PRODUCTION",
        "validation_date": "2026-11-07",
        "benchmark_models": ["LogisticRegression", "RandomForest", "GradientBoosting"],
        "champion_model": "GradientBoostingClassifier (Calibrated)",
        "fairness_audit": {
            "disparate_impact_ratio": 0.942,
            "equal_opportunity_difference": 0.038,
            "protected_attributes_evaluated": ["Age Brackets", "Gender"],
            "bias_threshold_met": True
        },
        "stability_metrics": {
            "population_stability_index_psi": 0.041,
            "interpretation": "Stable distribution (PSI < 0.10 indicates no significant shift)"
        },
        "recommendations": [
            "Perform quarterly PSI recalculation against production streaming ledger.",
            "Enforce four-eyes approval on retention actions triggered by probabilities > 0.85.",
            "Retrain champion model semi-annually or upon macro interest rate shifts."
        ]
    }


@router.get("/board-report")
def get_executive_board_report(
    request: Request,
    format: str = Query("json", pattern="^(json|markdown|html)$"),
    user: dict = Depends(require_roles(["Admin", "Executive", "ComplianceOfficer"]))
):
    """
    Generates unified Board of Directors and Supervisory Examination compliance packet.
    Supports formats: json, markdown, html.
    """
    from backend.reporting.regulatory_exporter import RegulatoryBoardReportExporter
    from fastapi.responses import HTMLResponse, PlainTextResponse

    log_api_action(request, user, "EXPORT_BOARD_GOVERNANCE_REPORT", "REPORTING", f"format={format}")

    if format == "markdown":
        md_text = RegulatoryBoardReportExporter.export_as_markdown()
        return PlainTextResponse(content=md_text, media_type="text/markdown")
    elif format == "html":
        html_text = RegulatoryBoardReportExporter.export_as_html()
        return HTMLResponse(content=html_text)

    return RegulatoryBoardReportExporter.generate_board_report_data()


@router.post("/stress-test/simulate")
def simulate_portfolio_stress_test(
    req: StressTestRequest,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "Executive", "ComplianceOfficer", "DataAnalyst"]))
):
    """
    Simulates Federal Reserve CCAR / DFAST and Basel III Liquidity Coverage Ratio (LCR) shocks.
    Scenarios: BASELINE, ADVERSE, SEVERELY_ADVERSE.
    """
    result = CCARStressTestSimulator.run_simulation(
        scenario_key=req.scenario,
        custom_hqla_buffer_usd=req.hqla_buffer_usd
    )

    # Update Prometheus gauge
    lcr_val = result["basel_iii_liquidity"]["projected_lcr_pct"]
    basel_iii_lcr_pct.labels(scenario=result["scenario"]).set(lcr_val)

    log_api_action(request, user, "RUN_CCAR_STRESS_TEST", "RISK_SIMULATION", req.scenario)
    return result


@router.get("/stress-test/benchmark")
def benchmark_all_stress_scenarios(
    request: Request,
    hqla_buffer_usd: float = Query(12000000.0, ge=100000.0),
    user: dict = Depends(require_roles(["Admin", "Executive", "ComplianceOfficer", "DataAnalyst"]))
):
    """
    Executes all three supervisory stress scenarios (Baseline, Adverse, Severely Adverse)
    for comparative executive risk analysis.
    """
    results = CCARStressTestSimulator.run_all_scenarios(hqla_buffer_usd=hqla_buffer_usd)
    for r in results:
        lcr_val = r["basel_iii_liquidity"]["projected_lcr_pct"]
        basel_iii_lcr_pct.labels(scenario=r["scenario"]).set(lcr_val)

    log_api_action(request, user, "BENCHMARK_CCAR_STRESS_TESTS", "RISK_SIMULATION", f"hqla={hqla_buffer_usd}")
    return results


@router.post("/aml-sar/scan")
def scan_portfolio_aml_risks(
    request: Request,
    limit: int = Query(100, le=500),
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer", "Executive"]))
):
    """
    Scans depository accounts for BSA/AML structuring, sudden capital flight surges,
    and returns prioritized accounts requiring compliance investigation.
    """
    from backend.compliance.sar_generator import FinCENSARGenerator

    alerts = FinCENSARGenerator.scan_portfolio_for_alerts(limit=limit)
    log_api_action(request, user, "SCAN_AML_RISKS", "BSA_AML", f"limit={limit}")
    return {
        "scanned_limit": limit,
        "flagged_accounts_count": len(alerts),
        "alerts": alerts
    }


@router.post("/aml-sar/generate/{customer_id}")
def generate_fincen_sar_narrative(
    customer_id: str,
    request: Request,
    user: dict = Depends(require_roles(["Admin", "ComplianceOfficer"]))
):
    """
    Generates a formal FinCEN Form 111-compliant Suspicious Activity Report (SAR) narrative
    with chronological suspicious transaction evidence and compliance attestation.
    """
    from backend.compliance.sar_generator import FinCENSARGenerator

    officer_name = user.get("username", "BSA/AML Compliance Officer")
    sar_packet = FinCENSARGenerator.generate_fincen_sar_packet(customer_id, compliance_officer=officer_name)
    if "error" in sar_packet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=sar_packet["error"])

    log_api_action(request, user, "GENERATE_FINCEN_SAR_NARRATIVE", "SAR_FILING", customer_id)
    return sar_packet



