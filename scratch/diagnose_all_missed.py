import sys
import pathlib
import numpy as np
import soundfile as sf
import pandas as pd
import tensorflow as tf

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
    EventState,
    OperatingMode
)

def run_diagnostics():
    det = DetectorImprovementV9()
    missed_df = pd.read_csv('e:/gunshot/gunshot/scratch/missed_with_paths.csv')
    print(f"Loaded {len(missed_df)} missed recordings for forensic audit.")

    records = []

    for idx, row in missed_df.iterrows():
        fname = row['filename']
        fpath = pathlib.Path("e:/gunshot/gunshot") / row['filepath']
        if not fpath.exists():
            fpath = pathlib.Path(row['filepath'])
        
        info = sf.info(str(fpath))
        dur = info.duration
        sr = info.samplerate
        audio, _ = sf.read(str(fpath), dtype='float32')
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

        # Pad if short
        win_size = 15360
        hop_size = 7680
        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)

        det.reset()
        win_details = []

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]

            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

            mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)

            # ML model scores
            wf_tensor = tf.convert_to_tensor(win, dtype=tf.float32)
            scores_raw, embeddings, _ = det.yamnet_model(wf_tensor)
            emb_mean = tf.reduce_mean(embeddings, axis=0, keepdims=True).numpy()
            p_mlp_real = float(det.classifier_head(emb_mean, training=False).numpy()[0, 0])
            p_cb = float(det.cb_model.predict_proba(emb_mean)[0, 1])
            p_lgb = float(det.lgb_model.predict_proba(emb_mean)[0, 1])
            p_xgb = float(det.xgb_model.predict_proba(emb_mean)[0, 1])

            raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            is_confirmed = (det.fsm.state == EventState.CONFIRMED)
            supp = det.suppression.apply_suppression(raw_score, ys, acoustics, is_confirmed)
            adj_score = supp["adjusted_score"]

            prev_state = det.fsm.state
            new_state, ev = det.fsm.step(adj_score, crest, w * 0.48, acoustics, mode)

            # Check single impulse conditions
            policy = det.fsm.get_policy_for_mode(mode)
            th_base = policy.get("threshold_base", 0.70)
            th_high = policy.get("threshold_high", 0.85)
            single_crest_std = policy.get("single_impulse_min_crest_db", 13.5)
            single_crest_high_conf = policy.get("single_impulse_high_conf_crest_db", 12.0)
            is_high_conf_qual = (
                adj_score >= th_high and
                crest >= single_crest_high_conf and
                (mode == OperatingMode.DEGRADED_OCCLUDED or (m2l >= 0.35 and cent >= 750.0))
            )
            single_allowed = policy.get("allow_single_impulse_exception", True) and ((crest >= single_crest_std) or is_high_conf_qual)

            pure_gun = ys.get(421, 0.0) # Gunshot
            cap_gun = ys.get(425, 0.0)
            explosion = ys.get(420, 0.0)
            whip = ys.get(466, 0.0)
            fireworks = max(ys.get(422, 0.0), ys.get(423, 0.0), ys.get(424, 0.0))

            win_details.append({
                "w": w,
                "crest": round(crest, 2),
                "peak": round(peak, 4),
                "cent": round(cent, 1),
                "hi": round(hi, 4),
                "mid": round(mid, 4),
                "lo": round(lo, 4),
                "m2l": round(m2l, 4),
                "p_mlp": round(p_mlp_real, 4),
                "p_cb": round(p_cb, 4),
                "p_lgb": round(p_lgb, 4),
                "p_xgb": round(p_xgb, 4),
                "pure_gun": round(pure_gun, 4),
                "explosion": round(explosion, 4),
                "raw_score": round(raw_score, 4),
                "adj_score": round(adj_score, 4),
                "suppressed": supp["suppressed"],
                "supp_cat": supp["category"],
                "mode": mode.value,
                "prev_state": prev_state.name,
                "new_state": new_state.name,
                "single_allowed": single_allowed,
                "is_high_conf_qual": is_high_conf_qual,
                "single_crest_std": single_crest_std,
                "th_base": th_base,
                "th_high": th_high,
                "event": ev is not None
            })

        # Summary for file
        max_adj = max(wd["adj_score"] for wd in win_details)
        max_raw = max(wd["raw_score"] for wd in win_details)
        max_crest = max(wd["crest"] for wd in win_details)
        max_peak = max(wd["peak"] for wd in win_details)
        best_win = max(win_details, key=lambda x: x["adj_score"])

        records.append({
            "filename": fname,
            "sub_category": row["sub_category"],
            "condition": row["condition_category"],
            "source": row["source_provenance"],
            "duration_sec": round(dur, 3),
            "n_wins": n_wins,
            "max_raw_score": max_raw,
            "max_adj_score": max_adj,
            "best_win_idx": best_win["w"],
            "crest_db": best_win["crest"],
            "peak_amp": best_win["peak"],
            "cent_hz": best_win["cent"],
            "hi": best_win["hi"],
            "mid": best_win["mid"],
            "lo": best_win["lo"],
            "m2l": best_win["m2l"],
            "pure_gun": best_win["pure_gun"],
            "explosion": best_win["explosion"],
            "p_mlp": best_win["p_mlp"],
            "p_cb": best_win["p_cb"],
            "p_lgb": best_win["p_lgb"],
            "p_xgb": best_win["p_xgb"],
            "suppressed": best_win["suppressed"],
            "supp_cat": best_win["supp_cat"],
            "mode": best_win["mode"],
            "fsm_state": best_win["new_state"],
            "single_allowed": best_win["single_allowed"],
            "is_high_conf_qual": best_win["is_high_conf_qual"],
            "th_base": best_win["th_base"],
            "th_high": best_win["th_high"]
        })

    diag_df = pd.DataFrame(records)
    diag_df.to_csv("e:/gunshot/gunshot/scratch/missed_positives_detailed_forensics.csv", index=False)
    print("Forensics complete. Saved to scratch/missed_positives_detailed_forensics.csv")

if __name__ == "__main__":
    run_diagnostics()
