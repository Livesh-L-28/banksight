"""
BankSight CLI Model Retraining & Champion-Challenger Auto-Promotion Script
Executes automated model retraining cycle on scheduled cron or CLI command:
1. Ingests fresh customer feature sets.
2. Trains Gradient Boosting Challenger model.
3. Benchmarks performance metrics vs. incumbent Champion.
4. Enforces Fair Lending 4/5ths Rule Disparate Impact Ratio.
5. Auto-promotes Challenger to Champion in the model registry.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from analytics.churn.retrainer import EnterpriseModelRetrainer  # noqa: E402


def main():
    print("=" * 70)
    print("🤖 BANKSIGHT MLOPS AUTOMATED MODEL RETRAINING & PROMOTION ENGINE")
    print("   OCC 2011-12 & Federal Reserve SR 11-7 Model Governance Protocol")
    print("=" * 70)

    print("\n[1/3] Ingesting latest customer features & training Challenger model...")
    result = EnterpriseModelRetrainer.retrain_and_evaluate(auto_promote=True)

    if not result.get("success"):
        print(f"❌ Retraining failed: {result.get('error')}")
        sys.exit(1)

    m = result["challenger_metrics"]
    f = result["fair_lending_audit"]

    print("\n[2/3] Model Evaluation & Champion Comparison:")
    print(f"   - Candidate Model ID: {result['model_id']}")
    print(f"   - Version Tag: {result['version_tag']}")
    print(f"   - Accuracy:    {m['accuracy']:.4f}")
    print(f"   - Precision:   {m['precision']:.4f}")
    print(f"   - Recall:      {m['recall']:.4f}")
    print(f"   - F1-Score:    {m['f1_score']:.4f}")
    print(f"   - ROC-AUC:     {m['roc_auc']:.4f} (Incumbent: {result['incumbent_roc_auc']:.4f})")
    print(f"   - Brier Score: {m['brier_score']:.4f}")

    print("\n[3/3] Regulatory Compliance & Promotion Gating:")
    print(f"   - Gender Disparate Impact Ratio (DIR): {f['disparate_impact_ratio_gender']:.3f}")
    print(f"   - 4/5ths Fair Lending Compliant:       {'YES (PASSED)' if f['compliant'] else 'NO (FAILED)'}")
    print(f"   - Auto-Promoted to Champion:          {'🏆 YES — PROMOTED' if result['promoted_to_champion'] else 'NO'}")

    print("\n" + "=" * 70)
    print("✅ RETRAINING & GOVERNANCE CYCLE COMPLETED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()

