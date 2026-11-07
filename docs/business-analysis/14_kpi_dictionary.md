# BankSight Enterprise KPI Dictionary
## Comprehensive Banking Metrics & Calculation Standards
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. Executive Summary & Governance Standards
This KPI Dictionary standardizes all metric formulas, operational definitions, data lineage, and business interpretations utilized throughout the **BankSight** platform, database views, and Power BI DAX expressions.

---

## 2. Core Banking KPI Directory

### 1. Total Customers ($N_{\text{cust}}$)
- **Definition:** The total count of distinct primary customer entities registered in the bank's core customer table.
- **Formula:**
  $$\text{Total Customers} = \sum \mathbf{1}_{c \in \text{Customers}}$$
- **SQL / Logic:** `SELECT COUNT(DISTINCT customer_id) FROM customers`
- **Cadence:** Real-time / Daily snapshot.
- **Business Interpretation:** Macro scale of the customer portfolio.

### 2. Active Customers ($N_{\text{active}}$)
- **Definition:** Customers with at least one active account and at least one financial or digital interaction within the trailing 90 days.
- **Formula:**
  $$\text{Active Customers} = \text{Count of customers where status} = \text{'Active'} \land (\text{days\_since\_last\_activity} \le 90)$$
- **Business Interpretation:** Core engaged customer base generating ongoing fee or interest income.

### 3. Inactive / Dormant Customers ($N_{\text{dormant}}$)
- **Definition:** Registered customers who have not executed any debit, credit, or digital login interaction within the trailing 90 days.
- **Formula:**
  $$\text{Inactive Customers} = \text{Total Customers} - \text{Active Customers}$$
- **Business Interpretation:** Attrition risk pool requiring automated reactivation nudges.

### 4. Customer Churn Rate ($R_{\text{churn}}$)
- **Definition:** The proportion of active customers who defected (closed all accounts or reached zero balance with no activity) during the observation period $T$.
- **Formula:**
  $$R_{\text{churn}} = \frac{N_{\text{churned customers in period } T}}{N_{\text{active customers at start of period } T}} \times 100\%$$
- **Benchmark:** Typical retail banking churn spans 12% to 22% annualized.

### 5. Customer Retention Rate ($R_{\text{retention}}$)
- **Definition:** The proportion of existing customers retained throughout the period.
- **Formula:**
  $$R_{\text{retention}} = 100\% - R_{\text{churn}} = \frac{N_{\text{end}} - N_{\text{new}}}{N_{\text{start}}} \times 100\%$$
- **Business Interpretation:** Fundamental health metric of customer relationship durability.

### 6. Total Deposit Volume ($V_{\text{dep}}$)
- **Definition:** Aggregate currency sum of all deposit credits across checking, savings, fixed, and recurring deposit accounts.
- **Formula:**
  $$V_{\text{dep}} = \sum_{i \in \text{Deposits}} \text{amount}_i$$
- **Currency:** USD (\$) (or configured local currency).

### 7. Total Withdrawal Volume ($V_{\text{wdr}}$)
- **Definition:** Aggregate currency sum of all debits, ATM cash withdrawals, POS purchases, and outbound transfers.
- **Formula:**
  $$V_{\text{wdr}} = \sum_{j \in \text{Withdrawals}} \text{amount}_j$$

### 8. Net Portfolio Balance ($B_{\text{net}}$)
- **Definition:** Total customer funds on deposit with the bank across all deposit-holding accounts.
- **Formula:**
  $$B_{\text{net}} = \sum_{a \in \text{Accounts}} \text{current\_balance}_a$$

### 9. Average Customer Balance ($\bar{B}$)
- **Definition:** Average cumulative balance held per active customer across all accounts.
- **Formula:**
  $$\bar{B} = \frac{\sum_{c} \text{Total Balance}_c}{N_{\text{active}}}$$

### 10. Average Revenue Per Customer (ARPU)
- **Definition:** Estimated net interest income (NII) plus fee income generated per customer over a 12-month period.
- **Formula:**
  $$\text{ARPU} = \frac{\text{Net Interest Spread} \times \text{Avg Balance} + \text{Total Fee Revenue}}{N_{\text{cust}}}$$
- **Analytical Approximation:** Modeled as $2.5\% \times \text{Average Balance} + \text{Annual Fee Revenue}$.

### 11. Customer Lifetime Value (CLV)
- **Definition:** Present value of net profit margin projected over the customer's anticipated remaining tenure.
- **Formula:**
  $$\text{CLV} = \frac{\text{ARPU} \times \text{Gross Margin \%}}{\text{Churn Rate} + \text{Discount Rate}} = \frac{\text{Annual Contribution}}{\text{Churn Rate} + d}$$
  *(where discount rate $d = 0.08$ and gross margin $= 75\%$)*.

### 12. High-Risk Customer Count ($N_{\text{high\_risk}}$)
- **Definition:** Total count of active customers whose calibrated churn probability exceeds the threshold ($P(\text{churn}) > 0.65$).
- **Business Interpretation:** Immediate priority target queue for retention management operations.

### 13. Retention Campaign Conversion Rate ($CR_{\text{ret}}$)
- **Definition:** Percentage of contacted high-risk retention cases that resulted in confirmed customer retention (`Status = 'Retained'`).
- **Formula:**
  $$CR_{\text{ret}} = \frac{N_{\text{Retained Cases}}}{N_{\text{Contacted Cases}}} \times 100\%$$

### 14. Marketing Campaign ROI ($ROI_{\text{camp}}$)
- **Definition:** Net return generated per dollar of marketing budget invested.
- **Formula:**
  $$ROI_{\text{camp}} = \frac{\text{Attributed Revenue} - \text{Campaign Cost}}{\text{Campaign Cost}} \times 100\%$$

### 15. Product Penetration Rate ($P_{\text{prod}}$)
- **Definition:** Percentage of total active customer base holding a specific banking product category.
- **Formula:**
  $$P_{\text{prod}} = \frac{N_{\text{customers holding product } p}}{N_{\text{total active customers}}} \times 100\%$$

### 16. Recency, Frequency, Monetary (RFM) Scores
- **Recency (R):** Quantile rank (1-5) of days elapsed since the customer's last debit transaction. (Rank 5 = most recent).
- **Frequency (F):** Quantile rank (1-5) of total transaction count within trailing 12 months. (Rank 5 = highest frequency).
- **Monetary (M):** Quantile rank (1-5) of aggregate transaction volume or average balance. (Rank 5 = highest value).
- **RFM Segment Assignment:**
  - *Champions / High Value:* $R \ge 4, F \ge 4, M \ge 4$
  - *Loyal Customers:* $R \ge 3, F \ge 3, M \ge 3$
  - *Potential Loyalists:* $R \ge 4, F \le 2, M \ge 3$
  - *New Customers:* $R \ge 4, F \le 2, M \le 2$
  - *At Risk:* $R \le 2, F \ge 3, M \ge 3$
  - *Dormant:* $R \le 2, F \le 2, M \le 2$

