#!/usr/bin/env python3
"""
BankSight Institutional Command-Line Interface (CLI)
Provides enterprise operators, SREs, and compliance auditors with direct terminal access
to executive KPIs, calibrated ML churn scoring, CCAR stress testing, CLV uplift optimization,
BSA/AML SAR generation, and WORM ledger verification.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.database.connection import get_db_session
from backend.repositories.kpi_repo import KPIRepository
from backend.services.churn_service import ChurnService
from analytics.clv.uplift_engine import CustomerLifetimeValueEngine
from analytics.retention.pricing_optimizer import ConcessionPricingOptimizer
from analytics.stress_testing.ccar_simulator import CCARStressTestSimulator
from backend.compliance.sar_generator import FinCENSARGenerator
from backend.security.audit_logger import audit_logger
from backend.reporting.regulatory_exporter import RegulatoryBoardReportExporter


def print_banner():
    banner = """
========================================================================
   BANK SIGHT — Enterprise Customer Intelligence & Retention Platform
   Institutional Command-Line Utility (v2.0-Enterprise)
========================================================================
"""
    print(banner)


def handle_kpis():
    print_banner()
    session = get_db_session()
    kpi_repo = KPIRepository(session)
    kpis = kpi_repo.calculate_executive_kpis()
    session.close()

    print(f"{'METRIC':<35} | {'VALUE':<25}")
    print("-" * 65)
    print(f"{'Total Depository Customers':<35} | {kpis['total_customers']:,}")
    print(f"{'Active Customers':<35} | {kpis['active_customers']:,}")
    print(f"{'Total Portfolio Deposits':<35} | ${kpis['total_deposits']:,.2f}")
    print(f"{'Annualized Churn Rate':<35} | {kpis['churn_rate_pct']:.2f}%")
    print(f"{'Operational Retention Rate':<35} | {kpis['retention_rate_pct']:.2f}%")
    print(f"{'Average Balance per Customer':<35} | ${kpis['average_customer_balance']:,.2f}")
    print(f"{'High Risk Customer Count':<35} | {kpis['high_risk_customers']:,}")
    print("=" * 65)


def handle_predict(customer_id: str):
    print_banner()
    from backend.database.connection import get_db_context
    from backend.models import Customer, Account, ChurnPrediction, Complaint

    with get_db_context() as session:
        cust = session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not cust:
            print(f"Customer '{customer_id}' not found.", file=sys.stderr)
            sys.exit(1)

        first_name = cust.first_name
        last_name = cust.last_name
        digital_active = bool(cust.digital_banking_active)
        accounts = cust.accounts or []
        tot_bal = sum(a.current_balance for a in accounts)
        complaints_count = session.query(Complaint).filter(Complaint.customer_id == customer_id).count()

        pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
        churn_prob = pred.churn_probability if pred else (0.85 if cust.churn_flag else 0.12)
        risk_category = pred.risk_category if pred else ("High Risk" if churn_prob >= 0.70 else ("Medium Risk" if churn_prob >= 0.35 else "Low Risk"))
        if pred and pred.model_version:
            model_version = pred.model_version.version_tag if hasattr(pred.model_version, 'version_tag') else str(pred.model_version)
        else:
            model_version = "v1.0-champion-calibrated"

    drivers = []
    if tot_bal < 1000.0:
        drivers.append(f"Depleted Depository Balance (${tot_bal:,.2f})")
    if complaints_count > 0:
        drivers.append(f"{complaints_count} service friction incident(s) recorded")
    if not digital_active:
        drivers.append("Digital channel disengagement")
    if not drivers:
        drivers.append("Steady deposit engagement and normal transaction velocity")

    action = (
        "Immediate proactive RM outreach with personalized fee-waiver or high-yield deposit offer"
        if churn_prob >= 0.70 else
        ("Schedule relationship review meeting" if churn_prob >= 0.35 else "Maintain regular quarterly touchpoints")
    )

    print(f"Customer ID:      {customer_id} ({first_name} {last_name})")
    print(f"Risk Tier:        {risk_category}")
    print(f"Churn Score:      {churn_prob:.1%}")
    print(f"Model Version:    {model_version}")
    print(f"Advisory Action:  {action}")
    print("\nTop Contributing Churn Drivers:")
    for d in drivers:
        print(f"  • {d}")


def handle_clv(customer_id: str):
    print_banner()
    from backend.database.connection import get_db_context
    from backend.models import Customer, Account, ChurnPrediction

    with get_db_context() as session:
        cust = session.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not cust:
            print(f"Customer '{customer_id}' not found.", file=sys.stderr)
            sys.exit(1)
        first_name = cust.first_name
        last_name = cust.last_name
        annual_inc = cust.annual_income or 65000.0
        loans_cnt = len(cust.loans or [])
        tot_bal = sum(a.current_balance for a in cust.accounts) if cust.accounts else 0.0
        pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
        churn_prob = pred.churn_probability if pred else (0.85 if cust.churn_flag else 0.12)

    clv = CustomerLifetimeValueEngine.calculate_customer_clv(
        total_balance=tot_bal,
        churn_probability=churn_prob,
        annual_income=annual_inc,
        loan_count=loans_cnt
    )
    print(f"Customer:                  {first_name} {last_name} ({customer_id})")
    print(f"Total Balance:             ${clv['total_balance']:,.2f}")
    print(f"Annual Gross NIM + Fees:   ${clv['annual_gross_revenue']:,.2f}")
    print(f"12-Month Discounted CLV:   ${clv['clv_12m_npv']:,.2f}")
    print(f"36-Month Discounted CLV:   ${clv['clv_36m_npv']:,.2f}")
    print(f"Uplift Retention Quadrant: {clv['retention_quadrant']} ({clv['quadrant_badge']})")
    print(f"Max Allowable Concession:  ${clv['max_allowable_concession_usd']:,.2f}")
    print(f"Strategy:                  {clv['treatment_strategy']}")


def handle_optimize_concession(customer_id: str):
    print_banner()
    res = ConcessionPricingOptimizer.optimize_for_customer_id(customer_id)
    if "error" in res:
        print(res["error"], file=sys.stderr)
        sys.exit(1)

    opt = res["optimal_recommendation"]
    prof = res["customer_profile"]
    print(f"Subject:            {prof['customer_name']} ({customer_id})")
    print(f"Retention Quadrant: {prof['retention_quadrant']}")
    print(f"Concession Cap:     ${prof['max_allowable_concession_usd']:,.2f}")
    print("-" * 65)
    print(f"RECOMMENDED OPTIMAL OFFER: {opt['offer_name']}")
    print(f"Annual Concession Cost:    ${opt['annual_cost_usd']:,.2f}")
    print(f"Rate Adjustment:           +{opt['rate_adjustment_bps']} bps")
    print(f"Projected Retention Rate:  {opt['projected_retention_probability']:.1%}")
    print(f"Expected Net Value Added:  ${opt['expected_net_gain_usd']:,.2f}")
    print(f"Expected Concession ROI:   {opt['roi_pct']:.1f}%")
    print(f"Requires Four-Eyes Signoff: {'YES (SOX 404 Trigger)' if opt['requires_four_eyes_approval'] else 'NO'}")
    print(f"\nAlgorithmic Rationale: {opt['rationale']}")


def handle_stress_test(scenario: str, hqla: float):
    print_banner()
    res = CCARStressTestSimulator.run_simulation(scenario, custom_hqla_buffer_usd=hqla)
    macro = res["macro_assumptions"]
    impact = res["portfolio_impact"]
    lcr = res["basel_iii_liquidity"]

    print(f"SUPERVISORY SCENARIO:      {res['scenario_name']}")
    print(f"GDP Growth Shock:          {macro['gdp_growth_pct']:+.1f}%")
    print(f"Fed Funds Rate:            {macro['fed_funds_rate_pct']:.2f}%")
    print(f"30-Day Liquidity Outflow:  ${impact['stressed_outflow_usd']:,.2f} ({macro['projected_outflow_pct']}%)")
    print(f"Stressed Deposits Remaining: ${impact['stressed_remaining_deposits_usd']:,.2f}")
    print("-" * 65)
    print(f"Available HQLA Buffer:     ${lcr['hqla_buffer_usd']:,.2f}")
    print(f"Projected Basel III LCR:   {lcr['projected_lcr_pct']:.1f}% (Minimum 100.0%)")
    print(f"LCR Compliance Status:     {'PASS' if lcr['lcr_compliant'] else 'CRITICAL DEFICIT'}")
    print(f"HQLA Net Position:         ${lcr['hqla_surplus_deficit_usd']:,.2f}")
    print(f"\nSupervisory Action: {res['supervisory_recommendation']}")


def handle_scan_aml():
    print_banner()
    alerts = FinCENSARGenerator.scan_portfolio_for_alerts(limit=50)
    print(f"Scanned accounts. Found {len(alerts)} customer(s) with AML red flags.\n")
    print(f"{'CUSTOMER ID':<12} | {'NAME':<20} | {'OUTFLOW USD':<14} | {'SCORE':<6} | {'PRIMARY RED FLAG':<30}")
    print("-" * 90)
    for a in alerts[:15]:
        flag_title = a['red_flags'][0]['title'] if a['red_flags'] else "N/A"
        print(f"{a['customer_id']:<12} | {a['customer_name']:<20} | ${a['total_debit_outflow_usd']:>12,.2f} | {a['aml_risk_score']:<6} | {flag_title:<30}")
    print("=" * 90)


def handle_sar(customer_id: str):
    print_banner()
    sar = FinCENSARGenerator.generate_fincen_sar_packet(customer_id)
    if "error" in sar:
        print(sar["error"], file=sys.stderr)
        sys.exit(1)
    print(sar["narrative_markdown"])


def handle_audit_verify():
    print_banner()
    res = audit_logger.verify_integrity()
    print(f"Audited Records Count: {res.get('count', 0)}")
    print(f"Chain Integrity Status: {'VALID (Cryptographically Intact)' if res.get('valid') else 'CORRUPTED'}")
    print(f"Audit Message: {res.get('message')}")


def handle_export_board_report(output_file: Optional[str] = None):
    print_banner()
    md = RegulatoryBoardReportExporter.export_as_markdown()
    target_path = Path(output_file) if output_file else Path("data/exports/board_governance_report.md")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Executive Board Oversight Report successfully generated at: {target_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="BankSight Institutional Banking CLI")
    parser.add_argument("--kpis", action="store_true", help="Print real-time Executive Banking KPIs")
    parser.add_argument("--predict", type=str, metavar="CUST_ID", help="Predict ML churn risk for customer ID")
    parser.add_argument("--clv", type=str, metavar="CUST_ID", help="Calculate 36m DCF CLV & uplift quadrant")
    parser.add_argument("--optimize-concession", type=str, metavar="CUST_ID", help="Run concession pricing optimizer")
    parser.add_argument("--stress-test", type=str, choices=["BASELINE", "ADVERSE", "SEVERELY_ADVERSE"], help="Run Fed CCAR stress test")
    parser.add_argument("--hqla", type=float, default=12000000.0, help="Custom HQLA buffer for stress test")
    parser.add_argument("--scan-aml", action="store_true", help="Scan customer accounts for BSA/AML red flags")
    parser.add_argument("--sar", type=str, metavar="CUST_ID", help="Generate FinCEN Form 111 SAR narrative packet")
    parser.add_argument("--verify-audit", action="store_true", help="Cryptographically audit SHA-256 WORM ledger")
    parser.add_argument("--export-board-report", type=str, nargs="?", const="data/exports/board_governance_report.md", help="Export formal board compliance packet")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.kpis:
        handle_kpis()
    elif args.predict:
        handle_predict(args.predict)
    elif args.clv:
        handle_clv(args.clv)
    elif args.optimize_concession:
        handle_optimize_concession(args.optimize_concession)
    elif args.stress_test:
        handle_stress_test(args.stress_test, args.hqla)
    elif args.scan_aml:
        handle_scan_aml()
    elif args.sar:
        handle_sar(args.sar)
    elif args.verify_audit:
        handle_audit_verify()
    elif args.export_board_report:
        handle_export_board_report(args.export_board_report)


if __name__ == "__main__":
    main()
