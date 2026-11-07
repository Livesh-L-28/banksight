"""
BankSight Institutional Stress Testing & Basel III Liquidity Simulation Engine
Simulates Federal Reserve CCAR / DFAST and Basel III Liquidity Coverage Ratio (LCR)
stress scenarios across the retail deposit portfolio:
1. Baseline Scenario
2. Adverse (Rate Hikes + Economic Downturn)
3. Severely Adverse (Liquidity Shock / Rapid Digital Deposit Flight)
"""

from typing import Dict, Any, List
import pandas as pd
from backend.database.connection import get_db_context
from backend.repositories.kpi_repo import KPIRepository


class CCARStressTestSimulator:
    """
    Executes macroeconomic stress testing on retail deposit stability,
    run-on-balance attrition velocity, and Basel III LCR compliance.
    """

    SCENARIOS = {
        "BASELINE": {
            "name": "Supervisory Baseline",
            "gdp_growth_pct": 2.1,
            "fed_funds_rate_pct": 4.50,
            "unemployment_rate_pct": 4.1,
            "deposit_beta": 0.35,
            "attrition_multiplier": 1.0,
            "liquidity_outflow_pct": 5.0
        },
        "ADVERSE": {
            "name": "Supervisory Adverse (Rate Hike + Mild Recession)",
            "gdp_growth_pct": -1.2,
            "fed_funds_rate_pct": 6.00,  # +150 bps shock
            "unemployment_rate_pct": 6.5,
            "deposit_beta": 0.65,
            "attrition_multiplier": 1.35,  # +35% attrition surge
            "liquidity_outflow_pct": 18.0
        },
        "SEVERELY_ADVERSE": {
            "name": "Supervisory Severely Adverse (Liquidity Shock & Capital Flight)",
            "gdp_growth_pct": -3.8,
            "fed_funds_rate_pct": 7.50,  # +300 bps shock
            "unemployment_rate_pct": 9.2,
            "deposit_beta": 0.90,
            "attrition_multiplier": 1.85,  # +85% attrition surge
            "liquidity_outflow_pct": 34.0
        }
    }

    @classmethod
    def run_simulation(cls, scenario_key: str = "ADVERSE", custom_hqla_buffer_usd: float = 12000000.0) -> Dict[str, Any]:
        """
        Simulates portfolio impact under the chosen macroeconomic stress scenario.
        """
        scenario_key = scenario_key.upper()
        if scenario_key not in cls.SCENARIOS:
            scenario_key = "ADVERSE"

        params = cls.SCENARIOS[scenario_key]

        with get_db_context() as session:
            kpi_repo = KPIRepository(session)
            kpis = kpi_repo.calculate_executive_kpis()

        total_deposits = kpis.get("total_deposits", 50000000.0)
        baseline_churn = kpis.get("churn_rate_pct", 12.0)

        # Stressed projections
        stressed_churn_rate = min(baseline_churn * params["attrition_multiplier"], 60.0)
        stressed_outflow_usd = total_deposits * (params["liquidity_outflow_pct"] / 100.0)
        stressed_remaining_deposits = total_deposits - stressed_outflow_usd

        # Basel III Liquidity Coverage Ratio (LCR = HQLA / Total Net Cash Outflows over 30 days)
        # Minimum regulatory threshold is 100.0%
        projected_lcr_pct = (custom_hqla_buffer_usd / max(stressed_outflow_usd, 1.0)) * 100.0
        lcr_compliant = projected_lcr_pct >= 100.0
        hqla_deficit_or_surplus = custom_hqla_buffer_usd - stressed_outflow_usd

        # Recommended Capital Retention Action
        if not lcr_compliant:
            recommendation = (
                f"CRITICAL DEFICIT: Under {params['name']}, liquidity outflows (${stressed_outflow_usd:,.2f}) "
                f"exceed HQLA buffer. Emergency deposit rate matching and RM capital retention campaign required "
                f"to protect ${abs(hqla_deficit_or_surplus):,.2f} in required liquidity."
            )
        else:
            recommendation = (
                f"ADEQUATE BUFFER: LCR projected at {projected_lcr_pct:.1f}% under {params['name']}. "
                f"Liquidity buffer remains compliant with Basel III minimums (≥100%)."
            )

        return {
            "scenario": scenario_key,
            "scenario_name": params["name"],
            "macro_assumptions": {
                "gdp_growth_pct": params["gdp_growth_pct"],
                "fed_funds_rate_pct": params["fed_funds_rate_pct"],
                "unemployment_rate_pct": params["unemployment_rate_pct"],
                "deposit_beta": params["deposit_beta"],
                "projected_outflow_pct": params["liquidity_outflow_pct"]
            },
            "portfolio_impact": {
                "baseline_deposits_usd": round(total_deposits, 2),
                "baseline_churn_rate_pct": round(baseline_churn, 2),
                "stressed_churn_rate_pct": round(stressed_churn_rate, 2),
                "stressed_outflow_usd": round(stressed_outflow_usd, 2),
                "stressed_remaining_deposits_usd": round(stressed_remaining_deposits, 2)
            },
            "basel_iii_liquidity": {
                "hqla_buffer_usd": round(custom_hqla_buffer_usd, 2),
                "projected_lcr_pct": round(projected_lcr_pct, 2),
                "regulatory_minimum_lcr_pct": 100.0,
                "lcr_compliant": lcr_compliant,
                "hqla_surplus_deficit_usd": round(hqla_deficit_or_surplus, 2)
            },
            "supervisory_recommendation": recommendation
        }

    @classmethod
    def run_all_scenarios(cls, hqla_buffer_usd: float = 12000000.0) -> List[Dict[str, Any]]:
        """Runs all three Fed CCAR scenarios for side-by-side executive benchmarking."""
        return [
            cls.run_simulation(s, custom_hqla_buffer_usd=hqla_buffer_usd)
            for s in ["BASELINE", "ADVERSE", "SEVERELY_ADVERSE"]
        ]

