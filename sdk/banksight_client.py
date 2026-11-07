"""
BankSight Official Python Client SDK
Production-grade client for interfacing with BankSight Enterprise REST API.
Supports OAuth2 Bearer token authentication, dual-authorization workflows,
streaming events ingestion, AI copilot briefings, and telemetry.
"""

import uuid
from typing import Dict, Any, Optional, List
import requests


class BankSightSDKError(Exception):
    """Base exception for all BankSight SDK errors."""
    pass


class AuthenticationError(BankSightSDKError):
    """Raised when authentication credentials fail or token is invalid."""
    pass


class PermissionDeniedError(BankSightSDKError):
    """Raised when the user role lacks required RBAC permission (HTTP 403)."""
    pass


class ResourceNotFoundError(BankSightSDKError):
    """Raised when a requested banking entity is not found (HTTP 404)."""
    pass


class APIResponseError(BankSightSDKError):
    """Raised when an API endpoint returns an unhandled HTTP error code."""
    def __init__(self, status_code: int, message: str, detail: Any = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.detail = detail


class BankSightClient:
    """
    Official Python Client for BankSight Enterprise Banking Intelligence API.

    Example Usage:
    ```python
    from sdk.banksight_client import BankSightClient

    client = BankSightClient(base_url="http://localhost:8000")
    client.login("admin_user", "AdminSecure2026!")

    kpis = client.get_executive_kpis()
    print("Total Customers:", kpis["total_customers"])

    briefing = client.generate_rm_briefing("CUST-000001")
    print("RM Briefing:", briefing["briefing_executive_summary"])
    ```
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        token: Optional[str] = None,
        timeout: float = 30.0,
        session: Optional[Any] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.session = session or requests.Session()
        self.current_user: Optional[Dict[str, Any]] = None

    def _headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "X-Client-SDK": "BankSight-Python-SDK-v2.0",
            "X-Correlation-ID": f"SDK-{uuid.uuid4().hex[:12]}"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        url = f"{self.base_url}{path}"
        req_headers = self._headers(headers)

        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=req_headers,
                timeout=self.timeout
            )
        except requests.RequestException as e:
            raise BankSightSDKError(f"Network transport error connecting to {url}: {e}") from e

        if resp.status_code == 401:
            raise AuthenticationError(f"Authentication failed (401): {resp.text}")
        elif resp.status_code == 403:
            raise PermissionDeniedError(f"Access forbidden (403): {resp.text}")
        elif resp.status_code == 404:
            raise ResourceNotFoundError(f"Resource not found (404): {resp.text}")
        elif not (200 <= resp.status_code < 300):
            try:
                err_detail = resp.json()
            except Exception:
                err_detail = resp.text
            raise APIResponseError(resp.status_code, resp.text, detail=err_detail)

        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return resp.text

    # --- Authentication ---

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticates against BankSight OAuth2 endpoint and stores Bearer token.
        """
        data = {"username": username, "password": password}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        result = self._request("POST", "/api/v1/auth/token", data=data, headers=headers)
        self.token = result.get("access_token")
        self.current_user = {
            "username": result.get("username"),
            "role": result.get("role"),
            "full_name": result.get("full_name")
        }
        return result

    def set_token(self, token: str) -> None:
        """Sets an external Bearer token directly."""
        self.token = token

    def get_current_user(self) -> Dict[str, Any]:
        """Fetches profile of currently authenticated user."""
        return self._request("GET", "/api/v1/auth/me")

    # --- System Health & Telemetry ---

    def get_health(self) -> Dict[str, Any]:
        """Returns API liveness status."""
        return self._request("GET", "/health")

    def get_ready(self) -> Dict[str, Any]:
        """Returns backend service readiness."""
        return self._request("GET", "/ready")

    def get_prometheus_metrics(self) -> str:
        """Fetches raw Prometheus metrics text."""
        return self._request("GET", "/metrics")

    # --- KPIs & Analytics ---

    def get_executive_kpis(self, branch_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetches top-level executive banking KPIs, optionally filtered by branch."""
        params = {"branch_id": branch_id} if branch_id else None
        return self._request("GET", "/api/v1/kpi/executive", params=params)

    def get_branch_rankings(self) -> List[Dict[str, Any]]:
        """Fetches branch ranking leaderboard and performance metrics."""
        return self._request("GET", "/api/v1/kpi/branch-rankings")

    def get_reconciliation_audit(self) -> Dict[str, Any]:
        """Executes transaction ledger integrity audit."""
        return self._request("GET", "/api/v1/kpi/reconciliation")

    # --- Customer Dossier & PII ---

    def get_customer_dossier(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieves 360 customer profile with demographics, financial accounts,
        and transaction history. Automatically applies dynamic PII masking for non-admin roles.
        """
        return self._request("GET", f"/api/v1/customers/{customer_id}")

    # --- Churn Machine Learning ---

    def predict_churn(self, customer_id: str, return_explanation: bool = True) -> Dict[str, Any]:
        """
        Executes calibrated ML churn prediction for a given customer.
        Returns risk score, risk level, contributing factors, and advisory action.
        """
        return self._request("POST", f"/api/v1/churn/predict-customer/{customer_id}")

    def get_risk_distribution(self) -> Dict[str, Any]:
        """Returns fleet-wide churn risk tier distribution counts."""
        return self._request("GET", "/api/v1/churn/risk-distribution")

    def retrain_model(self, auto_promote: bool = True) -> Dict[str, Any]:
        """
        Triggers MLOps candidate model retraining, Fair Lending DIR compliance verification,
        and automatic champion promotion.
        """
        params = {"auto_promote": auto_promote}
        return self._request("POST", "/api/v1/churn/retrain", params=params)

    # --- Operational Retention & Dual Authorization ---

    def get_retention_funnel(self) -> Dict[str, Any]:
        """Retrieves retention lifecycle funnel statistics and conversion rates."""
        return self._request("GET", "/api/v1/retention/funnel")

    def list_retention_cases(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Lists active retention cases with optional status or risk tier filtering."""
        params: Dict[str, Any] = {"limit": limit}
        if status:
            params["status_filter"] = status
        if risk_level:
            params["priority"] = risk_level
        return self._request("GET", "/api/v1/retention/cases", params=params)

    def submit_concession_offer(
        self,
        case_id: str,
        offer_name: str,
        financial_concession_value: float,
        rate_adjustment_bps: int = 0,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submits a customer retention concession offer.
        If financial_concession_value > $500 or rate_adjustment_bps > 50,
        it automatically triggers SOX 404 Four-Eyes dual-authorization hold in 'Pending Approval'.
        """
        payload = {
            "offer_name": offer_name,
            "financial_concession_value": financial_concession_value,
            "rate_adjustment_bps": rate_adjustment_bps,
            "notes": notes
        }
        return self._request("POST", f"/api/v1/retention/cases/{case_id}/submit-concession", json_data=payload)

    def review_concession_approval(
        self,
        case_id: str,
        approved: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes SOX 404 dual-authorization decision.
        Requires BranchManager, Executive, or Admin role with segregation of duties.
        """
        payload = {
            "approved": approved,
            "notes": notes
        }
        return self._request("POST", f"/api/v1/retention/cases/{case_id}/review-approval", json_data=payload)

    # --- Generative AI RM Copilot ---

    def generate_rm_briefing(self, customer_id: str) -> Dict[str, Any]:
        """
        Generates comprehensive AI Relationship Manager client meeting briefing,
        sentiment diagnosis, tactical talking points (Do's & Don'ts), and personalized outreach letter.
        """
        return self._request("POST", f"/api/v1/copilot/briefing/{customer_id}")

    # --- Real-Time Streaming & Attrition Triggers ---

    def stream_withdrawal_event(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects a real-time Core Banking withdrawal event into the attrition velocity engine.
        Evaluates run-on-balance conditions (>30% drop or >= $25k) and auto-escalates cases.
        """
        return self._request("POST", "/api/v1/streaming/events/withdrawal", json_data=event_payload)

    def stream_complaint_event(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Injects an omnichannel customer service complaint into the velocity engine.
        Triggers emergency escalation if severity is Critical or High.
        """
        return self._request("POST", "/api/v1/streaming/events/complaint", json_data=event_payload)

    def get_dispatched_webhooks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves history of dispatched real-time retention webhook notifications."""
        return self._request("GET", "/api/v1/streaming/webhooks", params={"limit": limit})

    # --- Model Governance & Compliance ---

    def get_governance_report(self) -> Dict[str, Any]:
        """
        Retrieves Fed SR 11-7 / OCC 2011-12 Model Risk Management audit report,
        including Fair Lending Disparate Impact Ratios and Population Stability Index (PSI).
        """
        return self._request("GET", "/api/v1/governance/sr11-7-summary")

    # --- Customer Lifetime Value (CLV) & Uplift Modeling ---

    def get_customer_clv(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieves discounted cash flow 12m/36m CLV, retention uplift quadrant,
        and maximum allowable financial concession cap for a specific customer.
        """
        return self._request("GET", f"/api/v1/clv/customer/{customer_id}")

    def get_portfolio_clv_summary(self) -> Dict[str, Any]:
        """
        Retrieves fleet-wide 36m CLV, value at risk, and quadrant distribution summary.
        """
        return self._request("GET", "/api/v1/clv/portfolio-summary")

    # --- Federal Reserve CCAR & Basel III Stress Testing ---

    def simulate_stress_test(
        self,
        scenario: str = "ADVERSE",
        hqla_buffer_usd: float = 12000000.0
    ) -> Dict[str, Any]:
        """
        Executes a Federal Reserve CCAR / Basel III Liquidity Coverage Ratio (LCR) simulation.
        Scenarios: 'BASELINE', 'ADVERSE', 'SEVERELY_ADVERSE'.
        """
        payload = {
            "scenario": scenario,
            "hqla_buffer_usd": hqla_buffer_usd
        }
        return self._request("POST", "/api/v1/governance/stress-test/simulate", json_data=payload)

    def benchmark_stress_testing(self, hqla_buffer_usd: float = 12000000.0) -> List[Dict[str, Any]]:
        """
        Executes all three supervisory stress scenarios (Baseline, Adverse, Severely Adverse)
        for side-by-side executive risk committee evaluation.
        """
        return self._request("GET", "/api/v1/governance/stress-test/benchmark", params={"hqla_buffer_usd": hqla_buffer_usd})

    # --- Core Banking Real-Time Webhooks ---

    def register_webhook(
        self,
        target_url: str,
        secret_key: str,
        subscribed_events: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registers an enterprise Core Banking webhook subscriber endpoint with HMAC-SHA256 signature verification.
        """
        payload = {
            "target_url": target_url,
            "secret_key": secret_key,
            "subscribed_events": subscribed_events,
            "description": description
        }
        return self._request("POST", "/api/v1/webhooks/subscriptions", json_data=payload)

    def list_webhooks(self) -> List[Dict[str, Any]]:
        """Lists active Core Banking webhook integration subscriptions."""
        return self._request("GET", "/api/v1/webhooks/subscriptions")

    def delete_webhook(self, subscription_id: str) -> Dict[str, Any]:
        """Revokes an enterprise Core Banking webhook subscription."""
        return self._request("DELETE", f"/api/v1/webhooks/subscriptions/{subscription_id}")

    def dispatch_test_webhook(
        self,
        event_type: str = "CAPITAL_FLIGHT",
        sample_payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Triggers a synthetic webhook test event to verify HMAC signing and receiver connectivity."""
        payload = {
            "event_type": event_type,
            "sample_payload": sample_payload
        }
        return self._request("POST", "/api/v1/webhooks/test-dispatch", json_data=payload)

    def get_webhook_deliveries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent webhook delivery logs with delivery receipts and timestamps."""
        return self._request("GET", "/api/v1/webhooks/deliveries", params={"limit": limit})

    # --- Algorithmic Concession Pricing Optimization ---

    def optimize_concession(self, customer_id: str) -> Dict[str, Any]:
        """
        Executes dynamic concession pricing optimization balancing retention probability uplift
        against annual concession cost to identify the profit-maximizing offer.
        """
        return self._request("POST", f"/api/v1/retention/optimize-concession/{customer_id}")

    # --- BSA/AML Compliance & FinCEN SAR Generation ---

    def scan_aml_risks(self, limit: int = 100) -> Dict[str, Any]:
        """
        Scans portfolio for Bank Secrecy Act / Anti-Money Laundering red flags,
        including rapid capital flight surges and structuring under CTR limits.
        """
        return self._request("POST", "/api/v1/governance/aml-sar/scan", params={"limit": limit})

    def generate_sar_narrative(self, customer_id: str) -> Dict[str, Any]:
        """
        Generates a formal FinCEN Form 111-compliant Suspicious Activity Report (SAR) narrative
        with chronological transaction evidence and compliance attestation.
        """
        return self._request("POST", f"/api/v1/governance/aml-sar/generate/{customer_id}")


