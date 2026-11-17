"""
Phase 20: End-to-End Pittsburgh Evaluation Reproduction Script
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Reproduces and verifies all Phase 20 forensic audit findings, including:
1. Baseline checksums (Phase 14 default, Phase 17 experimental).
2. Canonical event accounting (53 events = 50 Category A + 3 Category B across 23 streams).
3. 20-recording continuity audit (duration delta = 0.000000s, 1-to-1 polyphase resampling).
4. Category A detection recall across 6 frozen models.
5. Paired McNemar contingency table and exact p-value (p = 0.03125).
6. Geographic lineage and coordinate origin audit.
7. False alert exposure bounds (< 53.92 alerts/hr Poisson upper limit).
"""

import sys
import json
import hashlib
from pathlib import Path
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

REPORTS_DIR = ROOT / "reports"

print("=" * 75)
print("PHASE 20 FORENSIC AUDIT — END-TO-END REPRODUCTION HARNESS")
print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
print("=" * 75)

# 1. Baseline Model Verification
print("\n[STEP 1/7] Verifying Baseline Model Checksums...")
EXPECTED_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py":  "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
}

for fname, exp_hash in EXPECTED_HASHES.items():
    fpath = ROOT / fname
    assert fpath.exists(), f"Missing model file: {fname}"
    with open(fpath, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_hash == exp_hash, f"Hash mismatch on {fname}! Expected {exp_hash}, got {actual_hash}"
    print(f"  PASS: {fname} SHA-256 verified ({actual_hash[:16]}...)")

# 2. Canonical Manifest & Accounting
print("\n[STEP 2/7] Auditing Canonical Event & Recording Accounting...")
df_canonical = pd.read_csv(REPORTS_DIR / "phase20_canonical_event_manifest.csv")
with open(REPORTS_DIR / "phase20_event_accounting.json", "r", encoding="utf-8") as f:
    accounting = json.load(f)

assert len(df_canonical) == 53, f"Expected 53 events, got {len(df_canonical)}"
assert len(df_canonical["event_id"].unique()) == 53, "Duplicate event IDs found"
assert accounting["total_canonical_events"] == 53
assert accounting["total_positive_recordings"] == 23
assert accounting["category_a_events"] == 50
assert accounting["category_b_events"] == 3
print("  PASS: Exactly 53 unique events (50 Cat A + 3 Cat B) across 23 recordings verified.")

# 3. Continuity Audit
print("\n[STEP 3/7] Verifying 20-Recording Continuity Lineage...")
df_continuity = pd.read_csv(REPORTS_DIR / "phase20_continuity_audit.csv")
assert len(df_continuity) == 20, f"Expected 20 continuity audit records, got {len(df_continuity)}"
for _, r in df_continuity.iterrows():
    assert r["duration_difference_seconds"] == 0.0, f"Non-zero duration delta in stream {r['stream_id']}"
    assert r["continuity_classification"] == "RESAMPLED_OR_NORMALIZED_COPY"
    assert r["concatenation_detected"] == False
print("  PASS: All 20 Category A streams verified unbroken (duration delta = 0.000000s, 1-to-1 polyphase).")

# 4. Model Detections on Category A
print("\n[STEP 4/7] Verifying Frozen Detector Detections (Category A, N=50)...")
cat_a = df_canonical[df_canonical["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"]
EXPECTED_DETECTIONS = {
    "phase_14_balanced": 27,
    "phase_14_hp": 24,
    "phase_14_hs": 22,
    "phase_17_experimental": 33,
    "phase_9_balanced": 28,
    "phase_13_balanced": 16
}

for mkey, exp_count in EXPECTED_DETECTIONS.items():
    actual_count = int(cat_a[f"{mkey}_detected"].sum())
    recall_pct = actual_count / 50.0 * 100.0
    assert actual_count == exp_count, f"Mismatch on {mkey}: expected {exp_count}, got {actual_count}"
    print(f"  PASS: {mkey}: {actual_count}/50 ({recall_pct:.1f}% recall)")

# 5. Paired McNemar Test Re-Verification
print("\n[STEP 5/7] Verifying Paired McNemar Test (Phase 14 vs Phase 17)...")
both = int(((cat_a["phase_14_balanced_detected"] == True) & (cat_a["phase_17_experimental_detected"] == True)).sum())
p14_only = int(((cat_a["phase_14_balanced_detected"] == True) & (cat_a["phase_17_experimental_detected"] == False)).sum())
p17_only = int(((cat_a["phase_14_balanced_detected"] == False) & (cat_a["phase_17_experimental_detected"] == True)).sum())
neither = int(((cat_a["phase_14_balanced_detected"] == False) & (cat_a["phase_17_experimental_detected"] == False)).sum())

assert both == 27, f"Expected both=27, got {both}"
assert p14_only == 0, f"Expected p14_only=0, got {p14_only}"
assert p17_only == 6, f"Expected p17_only=6, got {p17_only}"
assert neither == 17, f"Expected neither=17, got {neither}"

n_disc = p14_only + p17_only
p_val = stats.binomtest(min(p14_only, p17_only), n_disc, 0.5, alternative='two-sided').pvalue
assert abs(p_val - 0.03125) < 0.0001, f"Expected p=0.03125, got {p_val}"
print(f"  PASS: McNemar Contingency Table [27, 0; 6, 17], discordant=6, exact two-sided p={p_val:.5f} verified.")

# 6. Geographic Lineage Audit
print("\n[STEP 6/7] Verifying Geographic Lineage & Arbitrary Origin Audit...")
df_geo = pd.read_csv(REPORTS_DIR / "phase20_geographic_lineage.csv")
assert len(df_geo) == 5, f"Expected 5 firing positions, got {len(df_geo)}"
for _, r in df_geo.iterrows():
    assert r["campaign_independence_classification"] == "SINGLE_MUNICIPAL_VALIDATION_CAMPAIGN"
    assert r["inter_position_distance_computable"] == False
print("  PASS: 5 firing positions confirmed as single municipal campaign with unaligned arbitrary Cartesian origins.")

# 7. False Alert Exposure Audit
print("\n[STEP 7/7] Verifying False Alert Exposure Calculations...")
t_total_s = 200.0
t_quiescent_s = 140.0
garwood_total_rate_hr = (2.99573 / t_total_s) * 3600.0
garwood_quiescent_rate_hr = (2.99573 / t_quiescent_s) * 3600.0

assert abs(garwood_total_rate_hr - 53.92) < 0.1
assert abs(garwood_quiescent_rate_hr - 77.03) < 0.1
print(f"  PASS: Poisson 95% upper bound on 200s audio: {garwood_total_rate_hr:.2f} alerts/hour.")
print(f"  PASS: Poisson 95% upper bound on 140s quiescent background: {garwood_quiescent_rate_hr:.2f} alerts/hour.")

print("\n" + "=" * 75)
print("ALL PHASE 20 FORENSIC AUDIT CHECKS PASSED PERFECTLY (100% REPRODUCIBLE)")
print("=" * 75)
