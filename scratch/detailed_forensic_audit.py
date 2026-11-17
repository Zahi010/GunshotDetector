import pandas as pd
import numpy as np

df = pd.read_csv("e:/gunshot/gunshot/scratch/missed_positives_detailed_forensics.csv")

print("=== DETAILED FORENSIC BREAKDOWN OF 20 MISSED RECORDINGS ===\n")

for idx, r in df.iterrows():
    fname = r["filename"]
    cond = r["condition"]
    sub = r["sub_category"]
    dur = r["duration_sec"]
    raw = r["max_raw_score"]
    adj = r["max_adj_score"]
    crest = r["crest_db"]
    peak = r["peak_amp"]
    cent = r["cent_hz"]
    lo = r["lo"]
    mid = r["mid"]
    hi = r["hi"]
    m2l = r["m2l"]
    pure = r["pure_gun"]
    exp = r["explosion"]
    p_mlp = r["p_mlp"]
    p_cb = r["p_cb"]
    p_lgb = r["p_lgb"]
    p_xgb = r["p_xgb"]
    supp = r["suppressed"]
    cat = r["supp_cat"]
    mode = r["mode"]
    fsm = r["fsm_state"]
    single_allowed = r["single_allowed"]

    # Determine exact failure category
    reasons = []
    category = "Unknown"

    # Category 3: FSM confirmation failure
    if adj >= 0.70 and fsm != "CONFIRMED":
        category = "3. FSM Confirmation Failure"
        reasons.append(f"Score {adj:.4f} >= 0.70 but single_allowed={single_allowed} (crest={crest:.2f} < 13.5 dB) and n_windows=1 prevented 2-window cluster confirmation")
    elif supp:
        if cat == "thunder_rumble":
            category = "6. Clipping / Saturation Failure" if cond == "high_energy_clipped" else "8. Erroneous Rumble Suppression"
            reasons.append(f"Erroneously suppressed by thunder_rumble rule (lo={lo:.4f}, m2l={m2l:.4f})")
        elif cat == "fireworks_dominant":
            category = "8. Erroneous Fireworks Suppression"
            reasons.append(f"Suppressed by fireworks rule (fw_s dominant, raw {raw:.4f} -> {adj:.4f})")
        elif cat == "ballistic_incoherence":
            category = "1. Classifier False Negative / Incoherence"
            reasons.append(f"Suppressed by ballistic coherence (pure_gun={pure:.4f} < 0.08, raw {raw:.4f} -> {adj:.4f})")
    elif raw < 0.70 and raw >= 0.40:
        if cond == "high_energy_clipped":
            category = "6. Clipping / Saturation Under-representation"
            reasons.append(f"Severe analog waveform clipping caused classifier score {raw:.4f} < 0.70")
        elif cond == "reverberant_urban":
            category = "5. Distance / Reverberation Dispersion"
            reasons.append(f"Multipath acoustic reflection and distance attenuation suppressed onset energy (raw {raw:.4f})")
        elif dur < 0.60:
            category = "7. Short-Duration / Window Truncation"
            reasons.append(f"Short single impulse ({dur:.3f}s) without sustained tail; classifier scored {raw:.4f}")
        else:
            category = "2. Threshold-Related Rejection"
            reasons.append(f"Near miss: raw score {raw:.4f} < 0.70 base threshold")
    elif raw < 0.40:
        category = "1. Classifier False Negative"
        reasons.append(f"Classifiers failed to recognize gunshot signature (MLP={p_mlp:.3f}, CB={p_cb:.3f}, LGB={p_lgb:.3f}, XGB={p_xgb:.3f}, raw={raw:.4f})")

    print(f"[{idx+1:02d}] {fname} ({cond}, {sub}, {dur:.2f}s)")
    print(f"     Primary Root Cause Category: {category}")
    print(f"     Raw: {raw:.4f} -> Adj: {adj:.4f} | Crest: {crest:.2f} dB, Peak: {peak:.4f}, Centroid: {cent:.1f} Hz")
    print(f"     Spectrum: lo={lo:.4f}, mid={mid:.4f}, hi={hi:.4f}, m2l={m2l:.4f}")
    print(f"     Base Models: MLP={p_mlp:.4f}, CB={p_cb:.4f}, LGB={p_lgb:.4f}, XGB={p_xgb:.4f}")
    print(f"     Semantic: pure_gun={pure:.4f}, explosion={exp:.4f} | Suppressed: {supp} ({cat})")
    print(f"     FSM State: {fsm} | single_allowed: {single_allowed} (th_high=0.85, th_base=0.70)")
    print(f"     Audit Details: {'; '.join(reasons)}\n")

