import sys
import os
import soundfile as sf
import librosa
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
    DetectorImprovementV10,
    EventState,
    OperatingMode,
    PURE_GUN_CLASSES,
    GLASS_CLASSES
)

print("=" * 70)
print("PHASE 55: DETAILED FORENSIC AUDIT OF 48 FALSE POSITIVES")
print("=" * 70)

pred_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
df = pd.read_csv(pred_csv)
fp_df = df[(df["ground_truth_label"] == 0) & (df["prediction"] == 1)].copy()
print(f"Total false positives to analyze: {len(fp_df)}")

det = DetectorImprovementV10()

fp_records = []

for idx, row in fp_df.iterrows():
    fpath = row["filepath"]
    audio, sr = sf.read(fpath, dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = audio.astype(np.float32)

    win_size = 15360
    hop_size = 7680
    if len(audio) < win_size:
        y_proc = np.pad(audio, (0, win_size - len(audio)))
        n_wins = 1
    else:
        y_proc = audio
        n_wins = 1 + int((len(audio) - win_size) // hop_size)

    det.reset()
    trigger_win = -1
    trigger_time_s = -1.0
    trigger_crest = 0.0
    trigger_cent = 0.0
    trigger_hi = 0.0
    trigger_lo = 0.0
    trigger_mid = 0.0
    trigger_m2l = 0.0
    trigger_raw = 0.0
    trigger_cal = 0.0
    trigger_adj = 0.0
    trigger_pure_gun = 0.0
    trigger_glass_s = 0.0
    trigger_supp = False
    trigger_supp_cat = "NONE"
    fsm_confirmed_at = -1

    for w in range(n_wins):
        st = w * hop_size
        en = st + win_size
        win = y_proc[st:en]

        feat, ys, acoustics = det.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        time_s = w * 0.48
        mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, time_s, w)

        raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        m_mean = float(feat[4])
        m_min = float(feat[6])
        m_std = float(feat[7])

        # BMCC
        cal_score = raw_score
        if det.consensus_cfg.get("enabled", True):
            min_prob = det.consensus_cfg.get("min_probability_agreement", 0.65)
            mean_th = det.consensus_cfg.get("mean_probability_threshold", 0.70)
            std_th = det.consensus_cfg.get("max_std_threshold", 0.12)
            min_crest = det.consensus_cfg.get("min_crest_db", 12.0)
            min_peak = det.consensus_cfg.get("min_peak_amplitude", 0.20)
            if m_min >= min_prob and crest >= min_crest and peak >= min_peak:
                cal_score = max(raw_score, m_mean)
            elif m_mean >= mean_th and m_std < std_th and crest >= min_crest and peak >= min_peak:
                cal_score = max(raw_score, m_mean)
            elif m_mean >= 0.68 and crest >= 18.0 and peak >= 0.40:
                cal_score = max(raw_score, m_mean)

        is_confirmed = (det.fsm.state == EventState.CONFIRMED)
        supp = det.apply_v9_suppression(cal_score, ys, acoustics, is_confirmed)
        adj_score = supp["adjusted_score"]
        cat = supp["category"]

        pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        glass_s = max(ys.get(c, 0.0) for c in GLASS_CLASSES)

        # Balloon rule check
        balloon_supp = False
        if not supp["suppressed"] and pure_gun < 0.35:
            if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                adj_score *= 0.25
                balloon_supp = True
                cat = "balloon_burst_impulse"

        # Glass rule check
        glass_supp = False
        if not supp["suppressed"] and glass_s >= 0.12 and cent >= 3000.0 and hi >= 0.30 and pure_gun < 0.30:
            adj_score *= 0.35
            glass_supp = True
            cat = "glass_shatter_calibrated"

        # C4 bypass
        c4_ground_blast = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
        if supp["suppressed"] and "rumble" in cat and c4_ground_blast:
            adj_score = cal_score
            cat = "c4_ground_blast_rescued"

        # FSM step
        st_before = det.fsm.state
        _, ev = det.fsm.step(adj_score, crest, time_s, acoustics, mode)
        st_after = det.fsm.state

        if st_after == EventState.CONFIRMED and fsm_confirmed_at < 0:
            fsm_confirmed_at = time_s
            trigger_win = w
            trigger_time_s = time_s
            trigger_crest = crest
            trigger_cent = cent
            trigger_hi = hi
            trigger_lo = lo
            trigger_mid = mid
            trigger_m2l = m2l
            trigger_raw = raw_score
            trigger_cal = cal_score
            trigger_adj = adj_score
            trigger_pure_gun = pure_gun
            trigger_glass_s = glass_s
            trigger_supp = (supp["suppressed"] or balloon_supp or glass_supp)
            trigger_supp_cat = cat

    # Failure mechanism explanation
    subcat = row["sub_category"]
    fail_mech = "Unknown"
    if "fireworks" in subcat:
        if trigger_pure_gun >= 0.20:
            fail_mech = f"YAMNet false semantic activation (pure_gun={trigger_pure_gun:.3f})"
        elif trigger_raw >= 0.75:
            fail_mech = f"Base ensemble overconfidence on sharp explosion (raw={trigger_raw:.3f})"
        else:
            fail_mech = f"Combustion rise-time heuristic missed (adj={trigger_adj:.3f}, crest={trigger_crest:.1f}dB)"
    elif "balloon" in subcat:
        reasons = []
        if trigger_cent < 3400.0: reasons.append(f"cent={trigger_cent:.0f}<3400")
        if trigger_hi < 0.70: reasons.append(f"hi={trigger_hi:.3f}<0.70")
        if trigger_lo > 0.015: reasons.append(f"lo={trigger_lo:.4f}>0.015")
        if trigger_pure_gun >= 0.35: reasons.append(f"pure_gun={trigger_pure_gun:.3f}>=0.35")
        fail_mech = f"Scalar balloon heuristic gate missed: {', '.join(reasons)}"
    elif "door" in subcat:
        fail_mech = f"Damped impact produced sufficient mid-freq energy (cent={trigger_cent:.0f}Hz, crest={trigger_crest:.1f}dB)"
    elif "hammer" in subcat:
        fail_mech = f"Sharp metallic onset matched ballistic crest factor (crest={trigger_crest:.1f}dB, raw={trigger_raw:.3f})"
    elif "thunder" in subcat:
        fail_mech = f"Thunderclap exhibited high-frequency crack (cent={trigger_cent:.0f}Hz, crest={trigger_crest:.1f}dB)"
    elif "glass" in subcat:
        fail_mech = f"Glass semantics below threshold or centroid below 3000Hz (glass_s={trigger_glass_s:.3f}, cent={trigger_cent:.0f}Hz)"
    else:
        fail_mech = f"Transient mimicked impulse profile (adj={trigger_adj:.3f}, crest={trigger_crest:.1f}dB)"

    fp_records.append({
        "fname": row["fname"],
        "title": row["title"],
        "sub_category": subcat,
        "peak_score": row["peak_score"],
        "trigger_time_s": round(trigger_time_s, 2),
        "trigger_crest_db": round(trigger_crest, 2),
        "trigger_cent_hz": round(trigger_cent, 1),
        "trigger_hi_ratio": round(trigger_hi, 4),
        "trigger_lo_ratio": round(trigger_lo, 4),
        "trigger_pure_gun": round(trigger_pure_gun, 4),
        "trigger_raw_score": round(trigger_raw, 4),
        "trigger_adj_score": round(trigger_adj, 4),
        "suppression_attempted": trigger_supp,
        "suppression_cat": trigger_supp_cat,
        "failure_mechanism": fail_mech
    })

fp_out_df = pd.DataFrame(fp_records)
out_csv = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis/negative_failure_analysis.csv")
fp_out_df.to_csv(out_csv, index=False)
print(f"Negative failure analysis written to {out_csv}")
print("\nFalse positives by sub-category:")
print(fp_out_df["sub_category"].value_counts())

