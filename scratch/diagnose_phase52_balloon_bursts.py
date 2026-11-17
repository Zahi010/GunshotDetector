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

def analyze_balloon_bursts():
    bb_dir = pathlib.Path("e:/gunshot/gunshot/data/background/hard_negatives/balloon_burst")
    files = sorted(list(bb_dir.glob("*.wav")))
    print(f"Found {len(files)} balloon burst recordings.")

    det = DetectorImprovementV8()
    records = []

    # Also load YAMNet class map if available
    class_map = {}
    class_map_path = pathlib.Path("e:/gunshot/gunshot/models/gunshot_yamnet_bundle/yamnet_class_map.csv")
    if class_map_path.exists():
        cm_df = pd.read_csv(class_map_path)
        for _, row in cm_df.iterrows():
            class_map[int(row['index'])] = row['display_name']

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

        # Physical temporal envelope analysis
        abs_audio = np.abs(audio)
        peak_val = np.max(abs_audio)
        peak_idx = int(np.argmax(abs_audio))
        peak_time_ms = (peak_idx / 16000.0) * 1000.0

        # Rise time (10% to 90% peak)
        t_10 = np.where(abs_audio >= 0.10 * peak_val)[0]
        t_90 = np.where(abs_audio >= 0.90 * peak_val)[0]
        rise_time_ms = ((t_90[0] - t_10[0]) / 16000.0 * 1000.0) if (len(t_10) > 0 and len(t_90) > 0 and t_90[0] >= t_10[0]) else 0.0

        # Decay time (peak to 10% peak)
        post_peak = abs_audio[peak_idx:]
        decay_idx = np.where(post_peak <= 0.10 * peak_val)[0]
        decay_time_ms = (decay_idx[0] / 16000.0 * 1000.0) if len(decay_idx) > 0 else (len(post_peak) / 16000.0 * 1000.0)

        # Total impulsive duration (time abs_audio > 10% peak)
        impulse_samples = np.where(abs_audio >= 0.10 * peak_val)[0]
        impulse_dur_ms = ((impulse_samples[-1] - impulse_samples[0]) / 16000.0 * 1000.0) if len(impulse_samples) > 0 else 0.0

        # Evaluate through V8 window by window
        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)

        win_records = []
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

            # Top YAMNet classes
            sorted_classes = sorted(ys.items(), key=lambda kv: kv[1], reverse=True)[:5]
            top_classes_str = ", ".join([f"{class_map.get(c, str(c))}:{s:.2f}" for c, s in sorted_classes])

            def _get_s(cls_list):
                return max(ys.get(c, 0.0) for c in cls_list)

            pure_gun = _get_s(PURE_GUN_CLASSES)
            gun_s = _get_s(GUN_CLASSES)
            bal_s = _get_s(BALLISTIC_CLASSES)
            pop_s = max(ys.get(430, 0.0), ys.get(429, 0.0))  # Pop, Boom
            burst_s = ys.get(428, 0.0)

            win_records.append({
                "window": w,
                "raw_score": raw_score,
                "adj_score": adj_score,
                "crest": crest,
                "cent": cent,
                "rolloff": rolloff,
                "hi": hi,
                "mid": mid,
                "lo": lo,
                "m2l": m2l,
                "pure_gun": pure_gun,
                "gun_s": gun_s,
                "bal_s": bal_s,
                "pop_s": pop_s,
                "burst_s": burst_s,
                "top_classes": top_classes_str,
                "event": ev is not None,
                "event_type": ev.get("trigger_type") if ev else None
            })

        max_adj = max(wr["adj_score"] for wr in win_records)
        peak_crest = max(wr["crest"] for wr in win_records)
        trigger_types = [wr["event_type"] for wr in win_records if wr["event_type"] is not None]

        # Top classes for peak window
        peak_win = max(win_records, key=lambda wr: wr["adj_score"])

        records.append({
            "filename": fname,
            "duration_sec": round(dur, 3),
            "peak_val": round(peak_val, 4),
            "rise_time_ms": round(rise_time_ms, 2),
            "decay_time_ms": round(decay_time_ms, 2),
            "impulse_dur_ms": round(impulse_dur_ms, 2),
            "max_adj_score": round(max_adj, 4),
            "peak_crest_db": round(peak_crest, 2),
            "cent_at_peak": round(peak_win["cent"], 1),
            "rolloff_at_peak": round(peak_win["rolloff"], 1),
            "hi_at_peak": round(peak_win["hi"], 4),
            "mid_at_peak": round(peak_win["mid"], 4),
            "lo_at_peak": round(peak_win["lo"], 4),
            "m2l_at_peak": round(peak_win["m2l"], 4),
            "pure_gun_at_peak": round(peak_win["pure_gun"], 4),
            "gun_s_at_peak": round(peak_win["gun_s"], 4),
            "bal_s_at_peak": round(peak_win["bal_s"], 4),
            "pop_s_at_peak": round(peak_win["pop_s"], 4),
            "top_classes_at_peak": peak_win["top_classes"],
            "triggered": len(trigger_types) > 0,
            "trigger_types": "; ".join(trigger_types)
        })

    df = pd.DataFrame(records)
    out_csv = pathlib.Path("e:/gunshot/gunshot/scratch/balloon_burst_forensics.csv")
    df.to_csv(out_csv, index=False)
    print(f"Exported balloon burst forensics to {out_csv}")

    print("\n--- Summary of Balloon Bursts ---")
    for r in records:
        print(f"{r['filename']}: Score={r['max_adj_score']:.4f}, Crest={r['peak_crest_db']:.1f} dB, "
              f"Rise={r['rise_time_ms']:.1f}ms, Decay={r['decay_time_ms']:.1f}ms, "
              f"Cent={r['cent_at_peak']:.0f}Hz, PureGun={r['pure_gun_at_peak']:.3f}, Bal={r['bal_s_at_peak']:.3f}, "
              f"Top={r['top_classes_at_peak']}")

if __name__ == "__main__":
    analyze_balloon_bursts()

