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
print("PHASE 55: DETAILED FORENSIC AUDIT OF 39 FALSE NEGATIVES")
print("=" * 70)

pred_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
df = pd.read_csv(pred_csv)
fn_df = df[(df["ground_truth_label"] == 1) & (df["prediction"] == 0)].copy()
print(f"Total false negatives to analyze: {len(fn_df)}")

det = DetectorImprovementV10()

failure_records = []

for idx, row in fn_df.iterrows():
    fpath = row["filepath"]
    audio, sr = sf.read(fpath, dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = audio.astype(np.float32)

    # Basic signal stats
    global_peak = float(np.max(np.abs(audio)))
    global_rms = float(np.sqrt(np.mean(audio**2) + 1e-12))
    global_rms_db = round(float(20 * np.log10(max(global_rms, 1e-6))), 2)

    # Noise estimate from lowest 20% energy frames
    win_len = 1024
    hop_len = 512
    n_frames = max(1, (len(audio) - win_len) // hop_len)
    frame_rms = [np.sqrt(np.mean(audio[i*hop_len : i*hop_len+win_len]**2) + 1e-12) for i in range(n_frames)]
    noise_floor = float(np.percentile(frame_rms, 20)) if frame_rms else 1e-6
    snr_est_db = round(float(20 * np.log10(max(global_peak, 1e-6) / max(noise_floor, 1e-6))), 2)

    # Window-by-window processing
    win_size = 15360
    hop_size = 7680
    if len(audio) < win_size:
        y_proc = np.pad(audio, (0, win_size - len(audio)))
        n_wins = 1
    else:
        y_proc = audio
        n_wins = 1 + int((len(audio) - win_size) // hop_size)

    det.reset()
    max_crest = -99.0
    max_raw_score = 0.0
    max_cal_score = 0.0
    max_adj_score = 0.0
    max_base_mean = 0.0
    suppression_reasons = set()
    states_visited = set()
    candidate_detected = False
    feature_valid = True

    for w in range(n_wins):
        st = w * hop_size
        en = st + win_size
        win = y_proc[st:en]

        try:
            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            if np.isnan(feat).any() or np.isinf(feat).any():
                feature_valid = False
        except Exception as e:
            feature_valid = False
            continue

        if crest > max_crest:
            max_crest = crest
        if crest >= 12.0 or peak >= 0.20:
            candidate_detected = True

        time_s = w * 0.48
        mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, time_s, w)

        raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        m_mean = float(feat[4])
        m_min = float(feat[6])
        m_std = float(feat[7])
        if m_mean > max_base_mean: max_base_mean = m_mean
        if raw_score > max_raw_score: max_raw_score = raw_score

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
        if cal_score > max_cal_score: max_cal_score = cal_score

        is_confirmed = (det.fsm.state == EventState.CONFIRMED)
        supp = det.apply_v9_suppression(cal_score, ys, acoustics, is_confirmed)
        adj_score = supp["adjusted_score"]
        cat = supp["category"]

        pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        glass_s = max(ys.get(c, 0.0) for c in GLASS_CLASSES)

        if not supp["suppressed"] and pure_gun < 0.35:
            if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                adj_score *= 0.25
                supp["suppressed"] = True
                cat = "balloon_burst_impulse"

        if not supp["suppressed"] and glass_s >= 0.12 and cent >= 3000.0 and hi >= 0.30 and pure_gun < 0.30:
            adj_score *= 0.35
            supp["suppressed"] = True
            cat = "glass_shatter_calibrated"

        c4_ground_blast = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
        if supp["suppressed"] and "rumble" in cat and c4_ground_blast:
            adj_score = cal_score
            supp["suppressed"] = False
            cat = "c4_ground_blast_rescued"

        if supp["suppressed"]:
            suppression_reasons.add(cat)
        if adj_score > max_adj_score: max_adj_score = adj_score

        # FSM step
        st_before = det.fsm.state.name
        det.fsm.step(adj_score, crest, time_s, acoustics, mode)
        st_after = det.fsm.state.name
        states_visited.add(st_after)

    # Classification of failure root cause
    reasons = []
    if not feature_valid:
        failure_type = "3. Feature extraction failure"
        stage_resp = "YAMNet/DSP Feature Extraction"
    elif global_peak < 0.20 or global_rms_db < -28.0 or max_crest < 12.0:
        failure_type = "2. Low-gain or dynamic-range failure"
        stage_resp = "Input Dynamic Range / Gain"
        reasons.append(f"Low peak ({global_peak:.3f}) or crest ({max_crest:.1f} dB)")
    elif max_cal_score >= 0.65 and max_adj_score < 0.65:
        failure_type = "5. Heuristic suppression rejection"
        stage_resp = f"Heuristic Suppression ({', '.join(suppression_reasons)})"
        reasons.append(f"Suppressed by {list(suppression_reasons)}")
    elif max_cal_score < 0.65:
        failure_type = "4. Classifier rejection"
        stage_resp = "Classifier Fusion Head (Score Below 0.65)"
        reasons.append(f"Raw {max_raw_score:.3f}, BMCC {max_cal_score:.3f}")
    elif "CONFIRMED" not in states_visited:
        failure_type = "6. FSM confirmation failure"
        stage_resp = "FSM Temporal/Persistence Logic"
        reasons.append(f"States visited: {list(states_visited)}")
    else:
        failure_type = "7. Multiple contributing causes"
        stage_resp = "Multi-Factor Failure"

    if len(reasons) > 1:
        failure_type = "7. Multiple contributing causes"

    failure_records.append({
        "fname": row["fname"],
        "title": row["title"],
        "uploader": row["uploader"],
        "sub_category": row["sub_category"],
        "duration_sec": row["duration_sec"],
        "global_peak": round(global_peak, 4),
        "global_rms_db": global_rms_db,
        "max_crest_db": round(max_crest, 2),
        "snr_est_db": snr_est_db,
        "candidate_detected": candidate_detected,
        "feature_valid": feature_valid,
        "max_base_mean": round(max_base_mean, 4),
        "max_raw_score": round(max_raw_score, 4),
        "max_cal_score": round(max_cal_score, 4),
        "max_adj_score": round(max_adj_score, 4),
        "suppression_triggered": bool(len(suppression_reasons) > 0),
        "suppression_reasons": "; ".join(suppression_reasons) if suppression_reasons else "NONE",
        "fsm_states_visited": "; ".join(states_visited),
        "primary_failure_classification": failure_type,
        "exact_stage_responsible": stage_resp
    })

fail_df = pd.DataFrame(failure_records)
out_csv = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis/positive_failure_analysis.csv")
fail_df.to_csv(out_csv, index=False)
print(f"Positive failure analysis saved to {out_csv}")
print("\nFailure breakdown by classification:")
print(fail_df["primary_failure_classification"].value_counts())

