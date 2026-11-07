# Enterprise Banking Business Rules
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Customer & Account Classification Rules

- **BR-ACT-01 Active Customer Status:**
  A customer is marked `Active` if they have at least one open account with a balance $\ge \$0.00$ and have performed a deposit, withdrawal, POS transaction, or authenticated digital banking session within the trailing 90 days.
- **BR-ACT-02 Inactive / Dormant Account Status:**
  An account with no customer-initiated financial activity (excluding automated bank interest credits or maintenance fees) for $> 90$ consecutive days is classified as `Dormant`. Dormant accounts are highlighted for outreach and excluded from active campaign solicitations.
- **BR-ACT-03 Customer Churn Definition:**
  A customer is classified as `Churned` if:
  1. All associated accounts are formally closed (`status = 'Closed'`), OR
  2. The cumulative balance across all accounts is $\le \$10.00$ AND no customer transactions have occurred for $\ge 180$ days.

---

## 2. Risk Classification & Churn Rules

- **BR-RSK-01 Calibrated Risk Thresholds:**
  Machine learning output probabilities $P(\text{churn}) \in [0, 1]$ are categorized into operational risk tiers:
  - **High Risk:** $P(\text{churn}) > 0.65$. Requires immediate retention case creation and RM assignment within 48 hours.
  - **Medium Risk:** $0.35 \le P(\text{churn}) \le 0.65$. Eligible for automated digital retention nurture campaigns (e.g. mobile app nudges, rate increase notifications).
  - **Low Risk:** $P(\text{churn}) < 0.35$. Standard customer service; prioritized for cross-sell rather than defensive retention.
- **BR-RSK-02 Advisory AI Mandate:**
  Algorithmic churn scores and cross-sell suggestions are strictly advisory. The platform shall never automatically close accounts, restrict customer funds, or execute binding financial contracts without explicit human confirmation.

---

## 3. Product Cross-Selling & Recommendation Rules

- **BR-PRD-01 Term / Fixed Deposit Eligibility:**
  Recommend a Fixed Deposit product if an active customer maintains an average checking/savings balance $> \$10,000$ with a balance volatility $< 15\%$ over the trailing 6 months, and does not currently hold a Fixed Deposit.
- **BR-PRD-02 Premium Credit Card Eligibility:**
  Recommend an upgraded credit card if customer annual income $> \$75,000$, total monthly spend $> \$2,500$, zero late payment history, and current credit card tenure $> 12$ months.
- **BR-PRD-03 Personal Loan / Line of Credit Opportunity:**
  Flag an advisory loan opportunity if customer tenure $> 24$ months, monthly net deposit flow is positive, debt-to-income indicator is low, and customer does not currently hold an active personal loan.

---

## 4. Retention Case Workflow Rules

- **BR-RET-01 Permitted Status Transitions:**
  Retention cases must strictly follow the state transition graph:
  - `Identified` $\to$ `Assigned`
  - `Assigned` $\to$ `Contacted`
  - `Contacted` $\to$ `Offer Proposed`
  - `Offer Proposed` $\to$ `Retained` OR `Not Retained`
  - `Retained` / `Not Retained` $\to$ `Closed`
- **BR-RET-02 Retention Offer Limits:**
  Relationship managers may only propose offers authorized by the customer's balance tier:
  - *Tier 1 ($< \$5,000$):* Standard fee waiver up to $\$50$.
  - *Tier 2 ($\$5,000 - \$50,000$):* Fee waiver up to $\$150$ or $+0.25\%$ APY savings boost for 6 months.
  - *Tier 3 ($> \$50,000$):* Dedicated Private Banker assignment, custom term deposit rate boost ($+0.50\%$ APY), and waived premium card annual fees.
