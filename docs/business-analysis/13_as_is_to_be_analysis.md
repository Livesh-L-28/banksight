# AS-IS vs. TO-BE Business Process Analysis
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Comparative Process Architecture

| Operational Dimension | AS-IS State (Legacy Banking Operations) | TO-BE State (BankSight Platform) | Business Impact / Benefit |
|---|---|---|---|
| **Churn Identification** | **Reactive:** Identified only after account closure, balance drop to zero, or customer complaint escalation. | **Predictive:** Machine learning models predict defection risk 60-90 days in advance with calibrated probabilities. | Preempts attrition while customer relationship is still salvageable; prevents loss of deposits. |
| **Customer Profiling** | **Fragmented:** RMs toggle between separate core banking green-screens, loan servicing systems, and CRM tabs. | **Unified Customer 360:** Comprehensive dossier integrating accounts, balances, complaints, timeline, and risk tiers in one view. | Cuts pre-call consultation prep time from 30 minutes to under 2 minutes per customer. |
| **Customer Segmentation** | **Static & Crude:** High-level balance brackets or broad demographic groupings without behavioral context. | **Dynamic & Multi-Tier:** Automated RFM scoring and empirical K-Means behavioral clustering. | Enables hyper-personalized messaging and precise product targeting. |
| **Retention Workflow** | **Ad-Hoc Spreadsheets:** Shared Excel workbooks emailed weekly without version control or accountability. | **Closed-Loop DB Workflow:** Database-persisted cases with auditable status states (`Identified` to `Retained/Not Retained`). | Enforces operational SLAs, eliminates duplicate contact, and measures retention ROI directly. |
| **Model Explainability** | **Black Box (or Non-Existent):** If analytics flags a risk, RMs are not told why, causing mistrust and non-adoption. | **Explainable AI:** Top contributing risk factors and actionable advisory recommendations displayed directly in RM workflow. | Boosts RM adoption of predictive alerts and ensures appropriate incentive selection. |
| **Campaign Attribution** | **Correlational Guesswork:** All product signups during campaign windows are credited to marketing without baseline adjustment. | **Attribution Modeling:** Documented multi-touch/last-touch attribution connecting responses to true incremental deposit growth. | Prevents wasted ad spend and optimizes marketing capital allocation. |
| **Management Reporting** | **Manual & Latent:** 4-5 analyst days per month spent extracting, formatting, and emailing static slide decks. | **Instant Multi-Format:** Real-time interactive dashboards with automated Excel, CSV, and PDF report downloads. | Eliminates analyst reporting overhead, empowering instant executive decision-making. |
