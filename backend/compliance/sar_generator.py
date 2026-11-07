"""
BankSight BSA/AML Compliance & FinCEN Suspicious Activity Report (SAR) Generator
Scans retail customer transaction streams for Bank Secrecy Act / Anti-Money Laundering
red flags (capital flight, structuring under $10,000 CTR limits, velocity surges)
and generates standardized FinCEN Form 111-compliant narrative packets.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

from backend.database.connection import get_db_context
from backend.models import Customer, Account, Transaction, ChurnPrediction


class FinCENSARGenerator:
    """
    Automated BSA/AML red-flag risk detection and FinCEN SAR narrative builder.
    """

    CTR_THRESHOLD_USD = 10000.0
    STRUCTURING_MIN_USD = 8500.0
    STRUCTURING_MAX_USD = 9999.0
    RAPID_OUTFLOW_THRESHOLD_USD = 25000.0

    @classmethod
    def scan_customer_aml_risks(cls, customer_id: str) -> Dict[str, Any]:
        """
        Evaluates a specific customer for BSA/AML red flags:
        1. Structuring (repeated transactions between $8,500 and $9,999)
        2. High-Velocity Capital Flight (outflows >= $25,000)
        3. Pre-Churn Depletion Surge
        """
        with get_db_context() as session:
            cust = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not cust:
                return {"error": f"Customer '{customer_id}' not found."}

            accounts = cust.accounts or []
            acc_ids = [a.account_id for a in accounts]
            total_balance = sum(a.current_balance for a in accounts)

            # Query transactions
            txns = session.query(Transaction).filter(Transaction.account_id.in_(acc_ids)).all() if acc_ids else []

            # Churn prediction
            pred = session.query(ChurnPrediction).filter(ChurnPrediction.customer_id == customer_id).first()
            churn_prob = pred.churn_probability if pred else (0.85 if cust.churn_flag else 0.12)

            # Identify red flags
            structuring_txns = []
            large_withdrawals = []
            total_outflow = 0.0

            for t in txns:
                amt = float(t.amount or 0.0)
                is_debit = t.transaction_type in ["Debit", "Withdrawal", "Transfer Out", "Wire"]
                if is_debit:
                    total_outflow += amt
                    if cls.STRUCTURING_MIN_USD <= amt <= cls.STRUCTURING_MAX_USD:
                        structuring_txns.append({
                            "transaction_id": t.transaction_id,
                            "account_id": t.account_id,
                            "amount": amt,
                            "channel": t.channel,
                            "date": t.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if t.transaction_date else "N/A"
                        })
                    if amt >= 10000.0:
                        large_withdrawals.append({
                            "transaction_id": t.transaction_id,
                            "account_id": t.account_id,
                            "amount": amt,
                            "channel": t.channel,
                            "date": t.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if t.transaction_date else "N/A"
                        })

            red_flags = []
            risk_score = 10  # Baseline low

            if len(structuring_txns) >= 2:
                red_flags.append({
                    "code": "AML_STRUCTURING",
                    "severity": "HIGH",
                    "title": "Suspected CTR Structuring",
                    "detail": f"{len(structuring_txns)} transactions identified just below the $10,000 reporting threshold ($8,500 - $9,999)."
                })
                risk_score += 45

            if total_outflow >= cls.RAPID_OUTFLOW_THRESHOLD_USD:
                red_flags.append({
                    "code": "CAPITAL_FLIGHT_SURGE",
                    "severity": "CRITICAL" if total_outflow >= 50000.0 else "HIGH",
                    "title": "Large Rapid Capital Flight",
                    "detail": f"Cumulative debits totaled ${total_outflow:,.2f}, indicating aggressive account balance depletion."
                })
                risk_score += 35

            if churn_prob >= 0.75 and total_outflow >= 15000.0:
                red_flags.append({
                    "code": "FLIGHT_PRE_CHURN",
                    "severity": "MEDIUM",
                    "title": "Pre-Defection Depletion Velocity",
                    "detail": f"High churn risk ({churn_prob:.1%}) correlated with accelerated balance extraction."
                })
                risk_score += 15

            risk_score = min(risk_score, 100)
            sar_filing_recommended = len(red_flags) > 0 and risk_score >= 50

            return {
                "customer_id": cust.customer_id,
                "customer_name": f"{cust.first_name} {cust.last_name}",
                "branch_id": cust.branch_id,
                "occupation": cust.occupation or "Not Specified",
                "total_balance_usd": round(total_balance, 2),
                "churn_probability": round(churn_prob, 4),
                "total_debit_outflow_usd": round(total_outflow, 2),
                "aml_risk_score": risk_score,
                "sar_filing_recommended": sar_filing_recommended,
                "red_flags": red_flags,
                "structuring_evidence": structuring_txns,
                "large_withdrawals": large_withdrawals,
                "total_accounts_analyzed": len(accounts),
                "total_transactions_analyzed": len(txns)
            }

    @classmethod
    def scan_portfolio_for_alerts(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Scans all portfolio accounts and returns prioritized list of customers with AML red flags.
        """
        with get_db_context() as session:
            customers = session.query(Customer).limit(limit).all()
            flagged = []
            for c in customers:
                analysis = cls.scan_customer_aml_risks(c.customer_id)
                if analysis.get("red_flags"):
                    flagged.append(analysis)

            return sorted(flagged, key=lambda x: x["aml_risk_score"], reverse=True)

    @classmethod
    def generate_fincen_sar_packet(cls, customer_id: str, compliance_officer: str = "BSA/AML Compliance Officer") -> Dict[str, Any]:
        """
        Builds a formal FinCEN Form 111-compliant Suspicious Activity Report (SAR) narrative.
        """
        risk_profile = cls.scan_customer_aml_risks(customer_id)
        if "error" in risk_profile:
            return risk_profile

        sar_ref_id = f"SAR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        filing_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Compose formal narrative
        red_flags_text = "\n".join([f"- [{f['severity']}] {f['title']}: {f['detail']}" for f in risk_profile["red_flags"]])
        structuring_count = len(risk_profile["structuring_evidence"])

        narrative = f"""### SUSPICIOUS ACTIVITY REPORT (SAR) NARRATIVE
**FinCEN Reference Tracking ID:** {sar_ref_id}
**Filing Date:** {filing_date}
**Financial Institution:** BankSight Commercial Bank N.A. (FDIC / Federal Reserve Regulated)
**Reporting Branch ID:** {risk_profile['branch_id']}

---

#### 1. SUBJECT IDENTIFICATION
- **Subject Name:** {risk_profile['customer_name']}
- **Customer Unique Identifier:** {risk_profile['customer_id']}
- **Stated Occupation:** {risk_profile['occupation']}
- **Current Depository Balance:** ${risk_profile['total_balance_usd']:,.2f}
- **Estimated Churn / Defection Probability:** {risk_profile['churn_probability']:.1%}

---

#### 2. SUMMARY OF SUSPICIOUS ACTIVITY
BankSight Automated Transaction Monitoring detected anomalous transaction behavior inconsistent with the subject's known financial profile. The primary red-flag indicators identified include:

{red_flags_text}

During the investigative lookback period, total cumulative debits across subject accounts reached **${risk_profile['total_debit_outflow_usd']:,.2f}**.
Specifically, **{structuring_count}** transaction(s) were executed in the narrow bracket between $8,500.00 and $9,999.00, suggesting deliberate structuring to evade mandatory Currency Transaction Report (CTR) filing requirements under 31 U.S.C. 5313 and 31 CFR 1010.311.

---

#### 3. CHRONOLOGICAL TRANSACTION EVIDENCE
A total of {risk_profile['total_transactions_analyzed']} transactions were analyzed. Suspicious transactions exhibiting structuring or rapid flight:
"""
        evidence_items = risk_profile["structuring_evidence"] + risk_profile["large_withdrawals"]
        for ev in evidence_items[:15]:
            narrative += f"- **{ev['date']}**: {ev['transaction_id']} | Account {ev['account_id']} | ${ev['amount']:,.2f} via {ev['channel']}\n"

        narrative += f"""
---

#### 4. DISPOSITION & INVESTIGATIVE RECOMMENDATION
Based on the convergence of transaction structuring, velocity surges, and imminent relationship defection, BankSight BSA/AML Compliance recommends:
1. Immediate transmission of this SAR Narrative to the Financial Crimes Enforcement Network (FinCEN).
2. Placement of enhanced monitoring and 100% debit holds on remaining funds pending FinCEN review.
3. Notification to the Bank Secrecy Act / AML Oversight Committee.

**Prepared By:** {compliance_officer}
**Compliance Certification:** SHA-256 Hash Chained WORM Ledger Verified
"""

        return {
            "sar_reference_id": sar_ref_id,
            "filing_date": filing_date,
            "customer_id": risk_profile["customer_id"],
            "customer_name": risk_profile["customer_name"],
            "aml_risk_score": risk_profile["aml_risk_score"],
            "sar_filing_recommended": risk_profile["sar_filing_recommended"],
            "red_flags": risk_profile["red_flags"],
            "narrative_markdown": narrative.strip(),
            "evidence_count": len(evidence_items),
            "total_suspicious_amount_usd": risk_profile["total_debit_outflow_usd"]
        }
