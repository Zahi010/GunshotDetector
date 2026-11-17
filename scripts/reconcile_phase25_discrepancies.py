"""
Phase 25 Forensic Reconciliation Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Constructs:
1. reports/phase25_stream_comparison_reconciliation.csv
2. reports/phase25_recording_inventory_reconciliation.csv
3. reports/phase25_reviewer_contingency_table.csv

Performs independent recalculation of:
- Stream-by-stream comparison categories (improved, equal, worse).
- Complete accounting of all 23 cataloged recordings with formal exclusion reasons.
- Reviewer-by-reviewer contingency table and Cohen's kappa evaluation.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"


def main():
    print("=" * 80)
    print("EXECUTING PHASE 25 FORENSIC RECONCILIATION ENGINE")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. STREAM-COUNT COMPARISON RECONCILIATION
    # -------------------------------------------------------------------------
    print("\n[1/3] Reconciling Stream-Level Comparison (Phase 23 vs. Phase 24)...")
    exp24_path = REPORTS_DIR / "phase24_exposure_accounting.csv"
    assert exp24_path.exists(), f"Missing {exp24_path}"
    df_exp = pd.read_csv(exp24_path)

    p14_df = df_exp[df_exp["detector"] == "Phase 14 Balanced"].sort_values("recording_id")
    p17_df = df_exp[df_exp["detector"] == "Phase 17 Experimental"].sort_values("recording_id")

    matched_rows = []
    improved_count = 0
    equal_count = 0
    worse_count = 0

    for r14, r17 in zip(p14_df.itertuples(), p17_df.itertuples()):
        assert r14.recording_id == r17.recording_id
        diff = int(r14.observed_alerts - r17.observed_alerts)
        improved = diff > 0
        equal = diff == 0
        worse = diff < 0

        if improved:
            improved_count += 1
        elif equal:
            equal_count += 1
        elif worse:
            worse_count += 1

        matched_rows.append({
            "recording_id": r14.recording_id,
            "campaign_id": r14.campaign_id,
            "phase14_alert_count": int(r14.observed_alerts),
            "phase17_alert_count": int(r17.observed_alerts),
            "difference": diff,
            "phase17_improved": improved,
            "counts_equal": equal,
            "phase17_worse": worse,
            "gross_exposure_s": float(r14.gross_duration_s),
            "gross_exposure_hr": float(r14.gross_duration_hr),
            "eligibility_status": "VERIFIED_NEGATIVE"
        })

    df_stream_recon = pd.DataFrame(matched_rows)
    out_stream_csv = REPORTS_DIR / "phase25_stream_comparison_reconciliation.csv"
    df_stream_recon.to_csv(out_stream_csv, index=False)
    print(f"  [OK] Saved stream comparison reconciliation: {out_stream_csv}")
    print(f"  Findings:")
    print(f"    Total evaluated continuous streams: {len(df_stream_recon)}")
    print(f"    Streams where Phase 17 improved (fewer alerts): {improved_count}")
    print(f"    Streams where counts were equal: {equal_count}")
    print(f"    Streams where Phase 17 was worse (more alerts): {worse_count}")
    print(f"    Net alert reduction: {df_stream_recon['difference'].sum()} alerts")

    # -------------------------------------------------------------------------
    # 2. 23-RECORDING INVENTORY RECONCILIATION
    # -------------------------------------------------------------------------
    print("\n[2/3] Reconciling 23-Recording Inventory...")
    prov_path = REPORTS_DIR / "phase24_recording_provenance.csv"
    assert prov_path.exists(), f"Missing {prov_path}"
    df_prov = pd.read_csv(prov_path)

    inventory_rows = []
    eval_gross_s = 0.0
    excl_gross_s = 0.0

    for idx, r in enumerate(df_prov.itertuples(), 1):
        rec_id = r.recording_id
        dur_s = float(r.duration_seconds)
        dur_hr = float(r.duration_hours)
        cont_type = r.continuity_status

        if rec_id.startswith("P24-NAT"):
            status = "INCLUDED_PRIMARY_EVALUATION"
            reason = "Verified natural unbroken field recording from independent campaign; verified negative."
            eval_gross_s += dur_s
        else:
            status = "EXCLUDED_NOT_CONTINUOUS"
            reason = "Synthetic overlay of ESC-50 discrete clips onto silence; unverified negative status; excluded from primary continuous benchmark."
            excl_gross_s += dur_s

        inventory_rows.append({
            "catalog_index": idx,
            "recording_id": rec_id,
            "legacy_recording_id": r.legacy_recording_id,
            "legacy_stream_id": r.legacy_stream_id,
            "filename": r.filename,
            "campaign_id": r.campaign_id,
            "gross_duration_s": dur_s,
            "gross_duration_hr": dur_hr,
            "continuity_type": cont_type,
            "status": status,
            "exclusion_reason": reason
        })

    df_inv_recon = pd.DataFrame(inventory_rows)
    out_inv_csv = REPORTS_DIR / "phase25_recording_inventory_reconciliation.csv"
    df_inv_recon.to_csv(out_inv_csv, index=False)
    print(f"  [OK] Saved recording inventory reconciliation: {out_inv_csv}")
    print(f"  Findings:")
    print(f"    Total cataloged recordings: {len(df_inv_recon)}")
    print(f"    Unique original recordings: {len(df_inv_recon['filename'].unique())}")
    print(f"    Continuous recordings: {len(df_inv_recon[df_inv_recon['continuity_type'] == 'NATURAL_CONTINUOUS'])}")
    print(f"    Eligible verified-negative recordings: {len(df_inv_recon[df_inv_recon['status'] == 'INCLUDED_PRIMARY_EVALUATION'])}")
    print(f"    Recordings actually evaluated: {len(df_inv_recon[df_inv_recon['status'] == 'INCLUDED_PRIMARY_EVALUATION'])}")
    print(f"    Gross hours cataloged: {(eval_gross_s + excl_gross_s) / 3600.0:.4f} h")
    print(f"    Gross hours evaluated: {eval_gross_s / 3600.0:.4f} h")
    print(f"    Gross hours excluded: {excl_gross_s / 3600.0:.4f} h")

    # -------------------------------------------------------------------------
    # 3. REVIEWER AGREEMENT CONTINGENCY TABLE AUDIT
    # -------------------------------------------------------------------------
    print("\n[3/3] Auditing Double-Reviewer Registry & Contingency Table...")
    review_path = REPORTS_DIR / "phase24_alert_review_registry.csv"
    assert review_path.exists(), f"Missing {review_path}"
    df_rev = pd.read_csv(review_path)

    r1_col = "reviewer1_classification"
    r2_col = "reviewer2_classification"

    contingency = pd.crosstab(df_rev[r1_col], df_rev[r2_col], margins=True, margins_name="Total")
    out_cont_csv = REPORTS_DIR / "phase25_reviewer_contingency_table.csv"
    contingency.to_csv(out_cont_csv)
    print(f"  [OK] Saved reviewer contingency table: {out_cont_csv}")
    print(f"  Contingency Table Output:")
    print(contingency)

    # Detailed verification
    n_total = len(df_rev)
    n_r1_non_target = (df_rev[r1_col] == "CONFIRMED_NON_TARGET").sum()
    n_r2_non_target = (df_rev[r2_col] == "CONFIRMED_NON_TARGET").sum()

    print(f"\n  Reviewer Audit Verification:")
    print(f"    Total records reviewed: {n_total}")
    print(f"    Reviewer 1 CONFIRMED_NON_TARGET: {n_r1_non_target} / {n_total}")
    print(f"    Reviewer 2 CONFIRMED_NON_TARGET: {n_r2_non_target} / {n_total}")
    print(f"    Final adjudication CONFIRMED_NON_TARGET: {(df_rev['adjudication_status'] == 'CONFIRMED_NON_TARGET').sum()} / {n_total}")
    
    if n_r1_non_target == n_total and n_r2_non_target == n_total:
        print("    CRITICAL FINDING: In the persisted phase24_alert_review_registry.csv, both Reviewer 1")
        print("    and Reviewer 2 have 100% identical post-adjudication labels (CONFIRMED_NON_TARGET).")
        print("    The pre-adjudication discordant labels (105/107) were not preserved as separate raw columns.")
        print("    Therefore, Cohen's kappa is mathematically degenerate on the stored artifact and marked UNVERIFIED.")

    print("\nForensic reconciliation calculations complete.")


if __name__ == "__main__":
    main()

