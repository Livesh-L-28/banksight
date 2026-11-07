"""
End-to-End Integration Test for BankSight Platform Workflow
Validates the complete lifecycle: Data Ingestion -> RFM & KMeans Segmentation ->
ML Churn Training -> Auto-Enrollment -> Retention Case Progression ->
Executive KPI Dynamic Aggregation -> Report Export.
"""

import pytest
from datetime import date
from backend.database.connection import get_db_session
from backend.services.segmentation_service import SegmentationService
from backend.services.churn_service import ChurnService
from backend.services.retention_service import RetentionService
from backend.repositories.kpi_repo import KPIRepository
from backend.services.reporting_service import ReportingService


def test_full_platform_lifecycle():
    # 1. Execute Segmentation (RFM + K-Means)
    seg_service = SegmentationService()
    seg_results = seg_service.run_all_segmentations(n_clusters=4, persist=True)
    assert len(seg_results["segmented_dataframe"]) == 1000
    assert len(seg_results["kmeans_distribution"]) == 4

    # 2. Train Churn Model & Score Portfolio
    churn_service = ChurnService()
    churn_results = churn_service.run_training_and_scoring(persist=True)
    assert "benchmark_results" in churn_results
    assert churn_results["champion_model_name"] in ["gradient_boosting", "random_forest", "logistic_regression"]

    # 3. Operational Retention Case Workflow
    ret_service = RetentionService()
    cases = ret_service.get_cases()
    assert len(cases) > 0

    target_case = cases[0]
    case_id = target_case["case_id"]

    # Assign RM
    ret_service.assign_relationship_manager(
        case_id=case_id,
        rm_id="RM-001",
        performed_by="Test Orchestrator",
        notes="Automated E2E Assignment"
    )

    # Progress status
    ret_service.update_case(
        case_id=case_id,
        new_status="Contacted",
        performed_by="RM Lead",
        notes="Client contacted via video call"
    )
    ret_service.update_case(
        case_id=case_id,
        new_status="Offer Proposed",
        performed_by="RM Lead",
        notes="Offered 4.50% high yield savings boost",
        proposed_offer="4.50% APY Savings"
    )
    ret_service.update_case(
        case_id=case_id,
        new_status="Retained",
        performed_by="RM Lead",
        notes="Offer accepted. Customer successfully retained."
    )

    # Verify action history
    history = ret_service.get_case_action_history(case_id)
    assert len(history) >= 4

    # 4. Executive KPI Recalculation
    session = get_db_session()
    kpi_repo = KPIRepository(session)
    kpis = kpi_repo.calculate_executive_kpis()
    session.close()

    assert kpis["total_customers"] == 1000
    assert kpis["total_deposits"] > 10000000.0
    assert kpis["churn_rate_pct"] > 0.0
    assert kpis["retention_rate_pct"] > 0.0

    # 5. Business Report Generation & Export
    rep_service = ReportingService()
    rep_data = rep_service.generate_report_data("Executive Banking Performance Report")
    csv_bytes = rep_service.export_csv(rep_data)
    xlsx_bytes = rep_service.export_excel(rep_data)
    pdf_bytes = rep_service.export_pdf(rep_data)

    assert len(csv_bytes) > 0
    assert len(xlsx_bytes) > 1000
    assert len(pdf_bytes) > 1000

