# Business Process Flow Specifications
## Project Name: BankSight — Banking Customer Intelligence & Retention Platform
**Document Version:** 1.0.0  
**Date:** 2026-11-07  

---

## 1. End-to-End Retention Management Process Flow

```mermaid
flowchart TD
    Start([Data Ingestion & Nightly ETL]) --> Extract[Extract Transactions, Complaints & Balances]
    Extract --> QualCheck{Data Quality Check Passed?}
    QualCheck -- No --> Quarantine[Log Rejected Records & Alert Admin]
    QualCheck -- Yes --> FeatEng[Compute Behavioral & RFM Features]
    
    FeatEng --> ModelScore[Run Machine Learning Churn Inference]
    ModelScore --> CalcProb[Compute Calibrated Churn Probability]
    
    CalcProb --> RiskBranch{Churn Probability}
    RiskBranch -- "P < 0.35" --> LowRisk[Classify: Low Risk - Standard Servicing]
    RiskBranch -- "0.35 <= P <= 0.65" --> MedRisk[Classify: Medium Risk - Monitor & Digital Nudge]
    RiskBranch -- "P > 0.65" --> HighRisk[Classify: High Risk - Priority Queue]
    
    HighRisk --> GenCase[Create Retention Case: Status = Identified]
    GenCase --> AssignRM[Assign Case to Branch Relationship Manager]
    AssignRM --> UpdateAssigned[Status: Assigned]
    
    UpdateAssigned --> RMReview[RM Reviews Customer 360 & Churn Drivers]
    RMReview --> Outreach[RM Conducts Client Consultation Outreach]
    Outreach --> StatusContacted[Status: Contacted]
    
    StatusContacted --> ProposeOffer[Propose Tailored Retention Incentive]
    ProposeOffer --> StatusOffered[Status: Offer Proposed]
    
    StatusOffered --> ClientDecision{Client Response}
    ClientDecision -- Accept Offer --> Retained[Status: Retained - Audit Log & Close]
    ClientDecision -- Decline / Defect --> Lost[Status: Not Retained - Capture Defection Reason]
    
    Retained --> DashboardUpdate[Real-Time Update: Retention KPI & Funnel]
    Lost --> DashboardUpdate
    Quarantine --> End([Process Terminated / Audited])
    LowRisk --> End
    MedRisk --> End
    DashboardUpdate --> End
```

---

## 2. Campaign Management & Attribution Process Flow

```mermaid
flowchart LR
    C1[Define Campaign Objective & Target Segment] --> C2[Allocate Budget & Assign Customers]
    C2 --> C3[Execute Multi-Channel Campaign Delivery]
    C3 --> C4[Capture Customer Responses & Product Originations]
    C4 --> C5[Apply Multi-Touch Attribution Engine]
    C5 --> C6[Calculate Net ROI, CPA & Incremental Balance]
    C6 --> C7[Generate Executive Campaign Performance Report]
```

