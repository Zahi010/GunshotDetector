import sys
import os
import pathlib
import json
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    DetectorImprovementV8,
    compute_physical_acoustic_features_v8,
    EventState,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    GLASS_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES,
    PURE_GUN_CLASSES
)

def analyze_door_slams():
    door_slam_dir = pathlib.Path("e:/gunshot/gunshot/data/background/hard_negatives/door_slam")
    files = sorted(list(door_slam_dir.glob("*.wav")))
    print(f"Found {len(files)} door slam recordings.")

    det = DetectorImprovementV8()
    records = []

    for fpath in files:
        fname = fpath.name
        audio, sr = sf.read(str(fpath))
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)

        det.reset()
        win_size = 15360
        hop_size = 7680
        dur = len(audio) / 16000.0

        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)

        file_events = []
        max_score = 0.0
        max_crest = 0.0

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            t_sec = w * 0.48

            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

            mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, t_sec, w)
            raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            is_confirmed = (det.fsm.state == EventState.CONFIRMED)
            supp = det.suppression.apply_suppression(raw_score, ys, acoustics, is_confirmed)
            adj_score = supp["adjusted_score"]

            state, ev = det.fsm.step(adj_score, crest, t_sec, acoustics, mode)

            if ev is not None:
                file_events.append(ev)

            max_score = max(max_score, adj_score)
            max_crest = max(max_crest, crest)

            def _get_s(cls_list):
                return max(ys.get(c, 0.0) for c in cls_list)

            pure_gun = _get_s(PURE_GUN_CLASSES)
            gun_s = _get_s(GUN_CLASSES)
            bal_s = _get_s(BALLISTIC_CLASSES)
            thun_s = _get_s(THUNDER_CLASSES)
            imp_s = _get_s(IMPACT_CLASSES)
            fw_s = _get_s(FIREWORKS_CLASSES)

            # Check transient override condition clauses
            clause1 = (m2l >= 0.40 and cent >= 750.0 and crest >= 16.0)
            clause2 = (pure_gun >= 0.12)
            clause3 = (peak >= 0.30 and crest >= 12.0 and cent >= 600.0)
            is_transient_override = (clause1 or clause2 or clause3)

            records.append({
                "filename": fname,
                "window_idx": w,
                "time_sec": round(t_sec, 3),
                "lo": round(lo, 4),
                "mid": round(mid, 4),
                "hi": round(hi, 4),
                "m2l": round(m2l, 5),
                "cent": round(cent, 1),
                "crest": round(crest, 2),
                "peak": round(peak, 4),
                "rms": round(rms, 5),
                "rolloff": round(rolloff, 1),
                "raw_score": round(raw_score, 4),
                "adj_score": round(adj_score, 4),
                "suppressed": supp["suppressed"],
                "supp_cat": supp["category"],
                "pure_gun": round(pure_gun, 4),
                "gun_s": round(gun_s, 4),
                "bal_s": round(bal_s, 4),
                "thun_s": round(thun_s, 4),
                "imp_s": round(imp_s, 4),
                "mode": mode.value,
                "fsm_state": state.value,
                "emitted_event": ev is not None,
                "event_type": ev.get("trigger_type") if ev else None,
                "clause1": clause1,
                "clause2": clause2,
                "clause3": clause3,
                "transient_override": is_transient_override
            })

    df = pd.DataFrame(records)
    out_csv = pathlib.Path("e:/gunshot/gunshot/scratch/door_slam_forensics.csv")
    df.to_csv(out_csv, index=False)
    print(f"Exported detailed door slam forensics to {out_csv}")

    # Summary by file
    print("\n--- Summary per Door Slam File ---")
    file_summary = []
    for fname, g in df.groupby("filename"):
        triggered = g["emitted_event"].any()
        peak_adj = g["adj_score"].max()
        peak_crest = g["crest"].max()
        mean_lo = g["lo"].mean()
        max_lo = g["lo"].max()
        min_m2l = g["m2l"].min()
        clause3_fired = g["clause3"].any()
        print(f"{fname}: Triggered={triggered}, Max Adj Score={peak_adj:.4f}, Max Crest={peak_crest:.1f} dB, Max lo={max_lo:.4f}, Min m2l={min_m2l:.5f}, Clause3={clause3_fired}")
        file_summary.append({
            "filename": fname,
            "triggered": triggered,
            "max_adj_score": peak_adj,
            "max_crest": peak_crest,
            "max_lo": max_lo,
            "min_m2l": min_m2l,
            "clause3_fired": clause3_fired
        })
    pd.DataFrame(file_summary).to_csv("e:/gunshot/gunshot/scratch/door_slam_file_summary.csv", index=False)

if __name__ == "__main__":
    analyze_door_slams()

